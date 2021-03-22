import logging

from flask import Flask, request
from flask_cors import CORS
from flask import jsonify
from functools import wraps

import time
from multiprocessing import Process

from aquilapy import Wallet, DB, Hub
from bs4 import BeautifulSoup

from transformers import pipeline
summarizer = pipeline("summarization")
qa = pipeline("question-answering")


app = Flask(__name__, instance_relative_config=True)

# Create a wallet instance from private key
wallet = Wallet("/ossl/private_unencrypted.pem")

# Connect to Aquila DB instance
db = DB("http://aquiladb", "5001", wallet)

# Connect to Aquila Hub instance
hub = Hub("http://aquilahub", "5002", wallet)

# Schema definition to be used
schema_def = {
    "description": "Wikipedia",
    "unique": "0",
    "encoder": "ftxt:https://ftxt-models.s3.us-east-2.amazonaws.com/wiki_100d_en.bin",
    "codelen": 100,
    "metadata": {
        "url": "string",
        "text": "string"
    }
}


# Craete a database with the schema definition provided
db_name = db.create_database(schema_def)

# Craete a database with the schema definition provided
db_name_ = hub.create_database(schema_def)

# Compress data
def compress_strings (db_name, strings_in):
    return hub.compress_documents(db_name, strings_in)

# Insert docs
def index_website (db_name, html_doc, url):
    paragraphs = get_paragraphs(html_doc)
    compressed = compress_strings(db_name, paragraphs)
    docs = []
    for idx_, para in enumerate(paragraphs):
        docs.append({
            "metadata": {
                "url": url, 
                "text": para
            },
            "code": compressed[idx_]
        })
    try:
        dids = db.insert_documents(db_name, docs)
        return True
    except Exception as e:
        logging.debug(e)
        return False

# generate summary
def summarize(text):
    return summarizer(text[:1024], min_length=5, max_length=20)[0]["summary_text"]

# generate QA
def QAgen(query, context):
    return qa(question=query, context=context)

# Search docs
def search_docs(db_name, query):
    compressed = compress_strings(db_name, [query])
    docs, dists = db.search_k_documents(db_name, compressed, 100)
    index = {}
    score = {}
    for idx_, doc in enumerate(docs[0]):
        metadata = doc["metadata"]
        if index.get(metadata["url"]):
            index[metadata["url"]] += 1
            score[metadata["url"]] += dists[0][idx_]
        else:
            index[metadata["url"]] = 1
            score[metadata["url"]] = dists[0][idx_]

    results_d = {}
    for key in index:
        results_d[key] = round(index[key] * score[key])

    results_d = {k: v for k, v in sorted(results_d.items(), key=lambda item: item[1], reverse=True)}
    summary_ret = summarize(docs[0]["metadata"]["text"])

    return results_d, summary_ret, QAgen(query, docs[0]["metadata"]["text"])
    
    # threshold = -1
    # for key in results_d:
        # print(key, results_d[key])
    #     if threshold == -1:
    #         threshold = round(results_d[key]*0.1)
    #     if results_d[key] > threshold:
    #         print(key)

# Get paragraphs given html document
def get_paragraphs(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    paras = []
    for para in soup.find_all("p"):
        text_data = para.text
        for txt in text_data.split("\n"):
            if txt.strip() != "":
                paras.append(" ".join(txt.strip().split()))
    return paras

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

@app.route("/index", methods=['POST'])
@authenticate()
def index_page ():
    """
    Index html page
    """

    # get parameters
    html_data = None
    url = None
    if extract_request_params(request).get("html") and extract_request_params(request).get("url"):
        html_data = extract_request_params(request)["html"]
        url = extract_request_params(request)["url"]
        print(url)

    if not html_data:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    global db_name
    status = index_website(db_name, html_data, url)
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

@app.route("/search", methods=['POST'])
def search ():
    """
    Search database for matches
    """

    # get parameters
    query = None
    if extract_request_params(request).get("query"):
        query = extract_request_params(request)["query"]

    if not query:
        # Build error response
        return {
                "success": False,
                "message": "Invalid parameters"
            }, 400

    global db_name
    urls, summary_r, ans_r = search_docs(db_name, query)

    # Build response
    return {
            "success": True,
            "result": {
                "urls": urls,
                "summary": summary_r,
                "ans": ans_r
            }
        }, 200


# Server starter
def flaskserver ():
    """
    start server
    """
    app.run(host='0.0.0.0', port=5000, debug=False)

# Enable CORS
CORS(app)

if __name__ == "__main__":
    flaskserver()