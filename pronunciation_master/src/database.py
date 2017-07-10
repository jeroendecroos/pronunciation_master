import mongo
from pymongo import MongoClient


def get_database():
    client = MongoClient()
    return client.pronunciation_master

