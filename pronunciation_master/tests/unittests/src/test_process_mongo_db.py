from mongomock import MongoClient

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import process_mongodb


class ParseLanguageTest(testcase.BaseTestCase):

    def test_no_section(self):
        text = ''
        ret = process_mongodb.parse_language(text)
        self.assertEqual(
            ret,
            [])

    def test_one_section(self):
        text = '===this_section===this_text'
        ret = process_mongodb.parse_language(text)
        self.assertEqual(
            ret,
            [{'section': 'this_section',
              'content': 'this_text'
              }])


class ParseDocTest(testcase.BaseTestCase):

    def test_no_section(self):
        ret = process_mongodb.parse_doc({'text': 'asdfasdf'})
        self.assertEqual(
            ret,
            [])

    def test_one_section(self):
        text = '==this-lang== ===this_section===this_text'
        document = {
            'text': text,
            'title': 'this_word',
            }
        ret = process_mongodb.parse_doc(document)
        self.assertEqual(
            ret,
            [{'section': 'this_section',
              'content': 'this_text',
              'language': 'this-lang',
              'word': 'this_word',
              }])


class ProcessDbTest(testcase.BaseTestCase):
    def setUp(self):
        self.client = MongoClient()
        self.db = getattr(self.client, 'pronunciation_test')

    def test_no_entries(self):
        process_mongodb.process_db(self.db)
        self.assertEqual(
            self.db.wiktionary_raw_subdivided.find_one(),
            None,
            )

    def test_no_entries_word(self):
        process_mongodb.process_db(self.db, word='null')
        self.assertEqual(
            self.db.wiktionary_raw_subdivided.find_one(),
            None,
            )

    def test_entries(self):
        text = '==this-lang== ===this_section===this_text'
        document = {
            'text': text,
            'title': 'this_word',
            }
        self.db.wiktionary_raw.insert_one(document)
        process_mongodb.process_db(self.db)
        self.assertEqual(
            self.db.wiktionary_raw_subdivided.find_one()['section'],
            'this_section',
              )
