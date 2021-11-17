import logging

from flask import Flask, request
from flask_cors import CORS
from functools import wraps

import html_cleanup as chtml

from services import logging as slog
slogging_session = slog.create_session()

from aquilapy import Wallet, DB, Hub

app = Flask(__name__, instance_relative_config=True)

# Create a wallet instance from private key
wallet = Wallet("/ossl/private_unencrypted.pem")

# Connect to Aquila DB instance
db = DB("http://aquiladb", "5001", wallet)

# Connect to Aquila Hub instance
hub = Hub("http://aquilahub", "5002", wallet)

# default database name
default_database_name = None

def create_database (user_id):

    # Schema definition to be used
    schema_def = {
        "description": "AquilaX-CE default user index",
        "unique": user_id,
        "encoder": "strn:msmarco-distilbert-base-tas-b",
        "codelen": 768,
        "metadata": {
            "url": "string",
            "text": "string"
        }
    }


    # Craete a database with the schema definition provided
    db_name = db.create_database(schema_def)

    # Craete a database with the schema definition provided
    db_name_ = hub.create_database(schema_def)

    return db_name, True

# Compress data
def compress_strings (db_name, strings_in):
    return hub.compress_documents(db_name, strings_in)

# Insert docs
def index_website (db_name, paragraphs, title, url):
    # add title as well to the index
    if title != "":
        paragraphs.append(title)
    compressed = compress_strings(db_name, paragraphs)
    docs = []
    for idx_, para in enumerate(paragraphs):
        v = compressed[idx_]

        docs.append({
            "metadata": {
                "url": url, 
                "text": para
            },
            "code": v
        })
    try:
        dids = db.insert_documents(db_name, docs)
        return True
    except Exception as e:
        logging.debug(e)
        return False

# Search docs
def search_docs(db_name, query):
    compressed = compress_strings(db_name, [query])
    docs, dists = db.search_k_documents(db_name, compressed, 100)
    index = {}
    score = {}

    for idx_, doc in enumerate(docs[0]):
        metadata = doc["metadata"]
        # -------------------------- exponential dampening ------------------------------
        if index.get(metadata["url"]):
            pass
        else:
            index[metadata["url"]] = 1
            score[metadata["url"]] = dists[0][idx_]

    results_d = {}
    
    for key in index:
        results_d[key] = score[key]

    results_d = {k: v for k, v in sorted(results_d.items(), key=lambda item: item[1], reverse=True)}

    return results_d

# Add authentication
def authenticate ():
    def decorator (f):
        @wraps(f)
        def wrapper (*args, **kwargs):
            # skip
            return f(*args, **kwargs)

        return wrapper
    return decorator

def extract_request_params (request):
    if not request.is_json:
        logging.error("Cannot parse request parameters")

        # request is invalid
        return {}

    # Extract JSON data
    data_ = request.get_json()

    return data_

@app.route("/", methods=['GET'])
def info ():
    """
    Check server status
    """

    # Build response
    return {
            "success": True,
            "message": "Aquila X is running healthy"
        }, 200

@app.route("/create", methods=['POST'])
@authenticate()
def create_db ():
    """
    Create a database on demand given a random unique seed
    """

    # get parameters
    user_id = None
    if extract_request_params(request).get("seed"):
        user_id = extract_request_params(request)["seed"]

    if not user_id:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    db_name, status = create_database(user_id)

    # Build response
    if status:
        return {
                "success": True,
                "databaseName": db_name
            }, 200
    else:
        return {
                "success": False,
                "message": "Invalid schema definition"
            }, 400

@app.route("/index", methods=['POST'])
@authenticate()
def index_page ():
    """
    Index html page
    """

    # get parameters
    html_data = None
    url = None
    db_name = default_database_name
    if extract_request_params(request).get("database"):
        db_name = extract_request_params(request)["database"]
    
    if extract_request_params(request).get("html") and extract_request_params(request).get("url"):
        html_data = extract_request_params(request)["html"]
        url = extract_request_params(request)["url"]

    if not html_data or not url or not db_name:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    # cleanup html
    chtml_data = chtml.process_html(html_data, url)
    thtml_data = chtml.trim_content(chtml_data["data"]["content"])["result"]

    # index html
    status = index_website(db_name, thtml_data, chtml_data["data"]["title"], url)

    # Build response
    if status:
        # logging
        if slogging_session != None:
            # index activity logging
            slog.put_log_index(slogging_session, db_name, url, html_data, 0)
            # metadata logging
            slog.put_url_summary(slogging_session, db_name, url, chtml_data["data"]["title"], chtml_data["data"]["author"], chtml_data["data"]["lead_image_url"], chtml_data["data"]["next_page_url"], "...".join(thtml_data))
        return {
                "success": True,
                "databaseName": db_name
            }, 200
    else:
        return {
                "success": False,
                "message": "Invalid schema definition"
            }, 400

@app.route("/search", methods=['POST'])
def search ():
    """
    Search database for matches
    """

    # get parameters
    query = None
    db_name = default_database_name
    if extract_request_params(request).get("database"):
        db_name = extract_request_params(request)["database"]
        
    if extract_request_params(request).get("query"):
        query = extract_request_params(request)["query"]

    if not query or not db_name:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    urls = search_docs(db_name, query)

    # logging
    if slogging_session != None:
        if len(urls) > 0:
            slog.put_log_search(slogging_session, db_name, query, list(urls.keys())[0])
        else:
            slog.put_log_search(slogging_session, db_name, query, "")

    # Build response
    return {
            "success": True,
            "result": urls
        }, 200

@app.route("/correct", methods=['POST'])
def correct ():
    """
    Correct matches
    """

    # get parameters
    query = None
    db_name = default_database_name
    url = None
    if extract_request_params(request).get("database"):
        db_name = extract_request_params(request)["database"]

    if extract_request_params(request).get("query") and extract_request_params(request).get("url"):
        query = extract_request_params(request)["query"]
        url = extract_request_params(request)["url"]

    if not query and not db_name and not url:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    # logging
    if slogging_session != None:
        slog.put_log_correct(slogging_session, db_name, query, url)

    # index correction
    status = index_website(db_name, [], query, url)

    # Build response
    return {
            "success": True
        }, 200

@app.route("/list", methods=['POST'])
def listall ():
    """
    List indexed urls
    """

    # get parameters
    page = None
    db_name = default_database_name
    limit = None
    if extract_request_params(request).get("database"):
        db_name = extract_request_params(request)["database"]

    if extract_request_params(request).get("page") and extract_request_params(request).get("limit"):
        page = extract_request_params(request)["page"]
        limit = extract_request_params(request)["limit"]

    if not page and not db_name and not limit:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    # get links
    if slogging_session != None:
        links = slog.get_all_url(slogging_session, db_name, page, limit)

    # Build response
    return {
            "success": True,
            "result": {
                "links": links
            }
        }, 200



@app.route("/urlsummary", methods=['POST'])
def summary ():
    """
    URL summary
    """

    # get parameters
    urls = None
    db_name = default_database_name
    if extract_request_params(request).get("database"):
        db_name = extract_request_params(request)["database"]

    if extract_request_params(request).get("urls"):
        urls = extract_request_params(request)["urls"]

    if not urls:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    summary_r = slog.get_url_summary(slogging_session, db_name, urls)

    # Build response
    return {
            "success": True,
            "result": {
                "summary": summary_r
            }
        }, 200


# Server starter
def flaskserver ():
    """
    start server
    """
    app.run(host='0.0.0.0', port=5003, debug=False)

# Enable CORS
CORS(app)

if __name__ == "__main__":
    # create default database
    db_name, status = create_database("default")
    if status:
        default_database_name = db_name
        logging.debug("Default DB name: " + default_database_name)
        # start server
        flaskserver()
