# this script is used to setup initial tables for logging of user behaviours

import sqlite3

database_location = "/data/ax_logs.db"

# create a cassandra session
def create_session ():
    # try connecting
    try:
        session = sqlite3.connect(database_location)
    except Exception as e:
        return None

    return session

def create_content_index_by_database (session):
    query = "CREATE TABLE IF NOT EXISTS content_index_by_database ( \
            id_ varint, \
            database_name varchar, \
            url text, \
            html text, \
            timestamp varint, \
            is_deleted int, \
            PRIMARY KEY ((database_name), timestamp, id_) );"
            
    try:
        return session.execute(query)
    except Exception as e:
        print(e)
        return False

def create_content_metadata_by_database (session):
    query = "CREATE TABLE IF NOT EXISTS content_metadata_by_database ( \
            id_ varint, \
            database_name varchar, \
            url text, \
            coverimg text, \
            title text, \
            author text, \
            timestamp varint, \
            outlinks text, \
            summary text, \
            PRIMARY KEY ((database_name), timestamp, id_) );"
            
    try:
        return session.execute(query)
    except Exception as e:
        print(e)
        return False

def create_search_history_by_database (session):
    query = "CREATE TABLE IF NOT EXISTS search_history_by_database ( \
            id_ varint, \
            database_name varchar, \
            query text, \
            url text, \
            timestamp varint, \
            PRIMARY KEY ((database_name), timestamp, id_) );"
            
    try:
        return session.execute(query)
    except Exception as e:
        print(e)
        return False

def create_search_correction_by_database (session):
    query = "CREATE TABLE IF NOT EXISTS search_correction_by_database ( \
            id_ varint, \
            database_name varchar, \
            query text, \
            url text, \
            timestamp varint, \
            PRIMARY KEY ((database_name), timestamp, id_) );"

    try:
        return session.execute(query)
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    session = create_session()
    print(create_content_index_by_database(session))
    print(create_content_metadata_by_database(session))
    print(create_search_history_by_database(session))
    print(create_search_correction_by_database(session))
    session.close()
