import argparse
import re

import mongodb


def process_db(database, debug_word=None):
    db = mongodb.default_local_db(
        database,
        drop_collection='wiktionary_ipa' if not debug_word else None,
        )
    query = debug_word and {'word': debug_word} or {}
    for document in db.wiktionary_raw_subdivided.find(query):
        entry = _process_document(document, debug_word)
        if entry:
            db.wiktionary_ipa.insert_one(entry)


def _process_document(document, debug_word=False):
    if 'section' not in document:
        raise Exception('"section" not in document {}'.format(document))
    if document['section'] == 'Pronunciation':
        ipa = process_ipa(document['content'])
        if debug_word:
            print ipa
            print document
        return {
            'language': document['language'],
            'word': document['word'],
            'IPA': ipa,
            }


def process_ipa(content):
    ipa_items = re.findall('{{IPA(.*?)}}', content)
    pronunciations = set()
    for ipa in ipa_items:
        ipa = re.sub('lang=[^|]+', '', ipa)
        item_pronunciations = re.split('/?\|?/?', ipa)
        pronunciations.update(item_pronunciations)
    if '' in pronunciations:
        pronunciations.remove(u'')
    return list(pronunciations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    parser.add_argument('--word', required=False)
    args = parser.parse_args()
    process_db(args.database, args.word)
