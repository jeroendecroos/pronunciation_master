import argparse
import xml.sax
import sys
import os
import codecs
import re
from pymongo import MongoClient



def process_db(database):
    client = MongoClient()
    db = getattr(client, database)
    to_collection = db.wiktionary_raw_subdivided
    to_collection.drop()
    for doc in db.wiktionary_raw.find({}):
        db.wiktionary_raw_subdivided.insert_many(
            parse_doc(doc))


def parse_doc(document):
    title_pattern = "(?<=[^=])(==[a-zA-Z- ]+==)(?=[^=])"
    items = []
    raw_items = re.split(title_pattern, document['text'])[1:]
    for i in range(0, len(raw_items), 2):
        language = raw_items[i]
        text = raw_items[i+1]
        language = language[2:-2]
        categories = parse_language(text)
        for category in categories:
            category.update({
                'word': document['title'],
                'language': language,
                })
            items.append(category)
    return items


def parse_language(text):
    section_pattern = "(?<=[^=])(===[0-9a-zA-Z- _]+===)(?=[^=])"
    items = []
    raw_items = re.split(section_pattern, text)[1:]
    for i in range(0, len(raw_items), 2):
        section = raw_items[i]
        text = raw_items[i+1]
        section = section[3:-3]
        items.append({
            'section': section,
            'content': text,
            })
    return items


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    args = parser.parse_args()
    process_db(args.database)
