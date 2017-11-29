import argparse
import re

import mongodb


def process_db(db, word=None):
    query = word and {'title': word} or {}
    for doc in db.wiktionary_raw.find(query):
        item = parse_doc(doc)
        if item:
            db.wiktionary_raw_subdivided.insert_many(
                item)
    if word:
        l = db.wiktionary_raw_subdivided.find({
            'word': word,
            })
        print [x for x in l]


def parse_doc(document):
    title_pattern = "(?<=[^=])(==[a-zA-Z- ]+==)(?=[^=])"
    items = []
    raw_items = re.split(title_pattern, ' '+document['text'])[1:]
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
    raw_items = re.split(section_pattern, ' '+text)[1:]
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
    parser.add_argument('--word', required=False)
    args = parser.parse_args()
    db = mongodb.default_local_db(
        args.database,
        drop_collection=not args.word and 'wiktionary_raw_subdivided')
    process_db(db, args.word)
