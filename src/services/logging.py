import logging

import sqlite3
import uuid, time, base64, hashlib

database_location = "/data/ax_logs.db"

# URL to id
def urls_to_ids (urls):
    return [ int(hashlib.sha1(url.encode("utf-8")).hexdigest(), 16) >> 96 for url in urls ]

# create a cassandra session
def create_session ():
    # try connecting
    try:
        session = sqlite3.connect(database_location, check_same_thread=False, isolation_level=None)
        session.row_factory = sqlite3.Row
    except Exception as e:
        return None

    return session

def get_log_index (session, database_name=None, url=None, html=None, is_deleted=0):
    # fetch index table
    # Query
    params_ = {
        "is_deleted": is_deleted
    }
    query = "SELECT * FROM content_index_by_database WHERE is_deleted=:is_deleted"
    if database_name != None:
        query += " and database_name=:database_name"
        params_["database_name"] = database_name
    if url != None:
        query += " and url=:url"
        params_["url"] = url
    if html != None:
        query += " and html=:html"
        params_["html"] = base64.b64encode(html.encode("utf-8")).decode("utf-8")
    query += ";"

    try:
        return [r for r in session.execute(query, params_).fetchall()]
    except Exception as e:
        logging.error(e)
        return []

def get_all_url (session, database_name, page=0, limit=100, is_deleted=0):
    # fetch all non deleted urls by page
    # Query
    if database_name != None:
        params_ = {
            "is_deleted": is_deleted,
            "database_name": str(database_name)
        }
        query = """SELECT * FROM content_index_by_database 
        WHERE is_deleted=:is_deleted and database_name=:database_name;"""

        try:
            urllst =  [{ "timestamp": r["timestamp"], "url": r["url"] } for r in session.execute(query, params_).fetchall()]

            # IMP TODO: remove below sorting and do sorting within DB itself
            return sorted(urllst, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logging.error(e)
            return []
    else:
        return []

def put_log_index (session, database_name, url, html, is_deleted=0):
    id_ = uuid.uuid1().int>>96  # truncating integer for SQLITE
    query = """INSERT INTO content_index_by_database (id_, database_name, url, html, timestamp, is_deleted) 
            VALUES(?, ?, ?, ?, ?, ?);"""
    params_ = (id_, str(database_name), str(url), base64.b64encode(html.encode("utf-8")).decode("utf-8"), int(time.time()), is_deleted)
    try:
        session.execute(query, params_)
    except Exception as e:
        logging.error(e)
        return False

    return True

def get_url_summary (session, db_name, urls_list):
    # fetch url summary
    ret_list = []
    # Query
    # ids_list = urls_to_ids(urls_list)
    if len(urls_list) > 0:
        for url in urls_list:
            query = """SELECT * FROM content_metadata_by_database WHERE url=:url 
            AND database_name=:db_name LIMIT 1;"""
            params_ = {
                "url": str(url),
                "db_name": str(db_name)
            }

            try:
                # merge results
                ret_list += [{ \
                    "title": r["title"], \
                    "author": r["author"], \
                    "url": r["url"], \
                    "coverimg": r["coverimg"], \
                    "summary": base64.b64decode(r["summary"].encode("utf-8")).decode("utf-8"), \
                    "outlinks": r["outlinks"] } \
                        for r in session.execute(query, params_)]
            except Exception as e:
                logging.error(e)

    return ret_list

def put_url_summary (session, database_name, url, title, author, coverimg, outlinks, summary):
    # create summary table for urls
    # precaution
    if not title:
        title = ""
    if not author:
        author = ""
    if not coverimg:
        coverimg = ""
    if not outlinks:
        outlinks = ""

    id_ = int((urls_to_ids([url])[0])/100) # truncating integer for SQLITE
    query = """INSERT INTO content_metadata_by_database (id_, database_name, url, coverimg, title, author, timestamp, outlinks, summary) 
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    params_ = (id_, str(database_name), str(url), str(coverimg), str(title), str(author), int(time.time()), str(outlinks), base64.b64encode(summary.encode("utf-8")).decode("utf-8"))
    try:
        session.execute(query, params_)
    except Exception as e:
        logging.error(e)
        return False

    return True

def get_log_search (session, database_name=None, query=None, url=None):
    # fetch search table
    # Query
    params_ = {}
    query_ = "SELECT * FROM search_history_by_database"

    if database_name != None or query != None or url != None:
        query_ += " WHERE"

    counter = 0
    if database_name != None:
        counter += 1
        query_ += " database_name=:database_name"
        params_["database_name"] = str(database_name)
    if url != None:
        if counter > 0:
            query_ += " and"
        counter += 1
        query_ += " url=:url"
        params_["url"] = str(url)
    if query != None:
        if counter > 0:
            query_ += " and"
        query_ += " query=:query"
        params_["query"] = str(query)
    query_ += ";"

    try:
        return [r for r in session.execute(query_, params_)]
    except Exception as e:
        logging.error(e)
        return []

def put_log_search (session, database_name, query, url):
    id_ = uuid.uuid1().int>>96  # truncating integer for SQLITE
    query_ = """INSERT INTO search_history_by_database (id_, database_name, query, url, timestamp) 
            VALUES(?, ?, ?, ?, ?);"""
    params_ = (id_, str(database_name), str(query), str(url), int(time.time()))
    try:
        session.execute(query_, params_)
    except Exception as e:
        logging.error(e)
        return False

    return True

def get_log_correct (session, database_name=None, query=None, url=None):
    # fetch correct table
    # Query
    params_ = {}
    query_ = "SELECT * FROM search_correction_by_database"

    if database_name != None or query != None or url != None:
        query_ += " WHERE"

    counter = 0
    if database_name != None:
        counter += 1
        query_ += " database_name=:database_name"
        params_["database_name"] = str(database_name)
    if url != None:
        if counter > 0:
            query_ += " and"
        counter += 1
        query_ += " url:url"
        params_["url"] = str(url)
    if query != None:
        if counter > 0:
            query_ += " and"
        query_ += " query=:query"
        params_["query"] = str(query)
    query_ += ";"

    try:
        return [r for r in session.execute(query_)]
    except Exception as e:
        logging.error(e)
        return []

def put_log_correct (session, database_name, query, url):
    id_ = uuid.uuid1().int>>96  # truncating integer for SQLITE
    query_ = """INSERT INTO search_correction_by_database (id_, database_name, query, url, timestamp) 
            VALUES(?, ?, ?, ?, ?);"""
    params_ = (id_, str(database_name), str(query), str(url), int(time.time()))
    try:
        session.execute(query_, params_)
    except Exception as e:
        logging.error(e)
        return False

    return True

