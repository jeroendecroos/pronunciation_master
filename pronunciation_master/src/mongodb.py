from pymongo import MongoClient


def default_local_db():
    client = MongoClient()
    db = getattr(client, 'pronunciation_master')
    return db
