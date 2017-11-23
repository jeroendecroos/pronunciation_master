from pymongo import MongoClient


def default_local_db(database='pronunciation_master', drop_collection=''):
    client = MongoClient()
    db = getattr(client, database)
    if drop_collection:
        getattr(db, drop_collection).drop()
    return db
