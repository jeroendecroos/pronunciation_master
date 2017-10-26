import argparse
import xml.sax
import sys
import os
import codecs
import re
from pymongo import MongoClient



def process_db(database, word=None):
    client = MongoClient()
    db = getattr(client, database)
    if not word:
        db.wiktionary_ipa.drop()
    query = word and {'word': word} or {}
    for document in db.wiktionary_raw_subdivided.find(query):
        if not 'section' in document:
            import pdb; pdb.set_trace()
        if document['section'] == 'Pronunciation':
            ipa = process_ipa(document['content'])
            if word:
                print ipa
                print document
            db.wiktionary_ipa.insert_one({
                'language': document['language'],
                'word': document['word'],
                'IPA': ipa,
                })



def process_ipa(content):
    pronunciations = re.findall('{{.*IPA\|/?([^/|\n]*)/?\|?.*}}', content)
    return pronunciations


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    parser.add_argument('--word', required=False)
    args = parser.parse_args()
    process_db(args.database, args.word)
