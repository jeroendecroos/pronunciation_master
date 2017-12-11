import mock
from mongomock import MongoClient
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import process_mongodb_ipa


class FilterPronunciationsTest(testcase.BaseTestCase):
    @params(
        ("ik",
            (u'\n* {{rhymes|\u026ak|lang=nl}}\n*'
             u'{{audio|Nl-ik.ogg|audio|lang=nl}}\n*'
             u'{{IPA|/\u026ak/|lang=nl}} (stressed),'
             u'{{IPA|/\u0259k/|lang=nl}} (unstressed)\n\n'
             ),
            [u'\u026ak', u'\u0259k']),
        ("femme",
            u'\n* {{IPA|/f\u025bm/|lang=en}}\n\n',
            [u'f\u025bm']),
        ("het",
            (u'\n* {{rhymes|\u0259t|\u025bt|lang=nl}}\n* {{a|BE}}'
             u'{{IPA|/\u0259t/|/\u0266\u0259t/|lang=nl}}\n*'
             u'{{audio|Nl-het (Belgium).ogg|audio (Belgium)|lang=nl}}\n*'
             u'{{a|NL}} {{IPA|lang=nl|/\u0259t/}} {{qualifier|usually}},'
             u'{{IPA|lang=nl|/\u0266\u025bt/}} {{qualifier|when stressed}}\n*'
             u'{{audio|Nl-het.ogg|audio (Netherlands)|lang=nl}}\n\n'
             ),
            [u'\u0259t', u'\u0266\u0259t', u'\u0266\u025bt']),

        )
    def test_process_ipa(self, _, pronunciation_section, expected):
        assert isinstance(pronunciation_section, basestring)
        result = process_mongodb_ipa.process_ipa(pronunciation_section)
        self.assertItemsEqual(result, set(expected))


@mock.patch('pronunciation_master.src.process_mongodb_ipa._process_document')
class ProcessDbTest(testcase.BaseTestCase):
    def setUp(self):
        process_mongodb_ipa.MongoClient = MongoClient
        self.client = process_mongodb_ipa.MongoClient()
        self.db = getattr(self.client, 'pronunciation_test')

    def test_no_entries(self, process):
        process.return_value = {'test': 1}
        self.wiktionary = self.db.wiktionary_ipa
        process_mongodb_ipa.process_db(self.db)
        self.assertEqual(
            self.db.wiktionary_ipa.find_one(),
            None,
            )

    def test_entries(self, process):
        self.db.wiktionary_raw_subdivided.insert_one({
            'section': 'Pronunciation',
            })
        process.return_value = {'test': 1}
        self.wiktionary = self.db.wiktionary_ipa
        process_mongodb_ipa.process_db(self.db)
        self.assertEqual(
            self.db.wiktionary_ipa.find_one()['test'],
            1,
            )


class ProcessDocumentTest(testcase.BaseTestCase):
    def test_no_section(self):
        with self.assertRaises(Exception):
            process_mongodb_ipa._process_document({})

    def test_one_section(self):
        document = {
            'section': 'Pronunciation',
            'content': u'{{IPA|/fem/|lang=en}}',
            'language': 'ba',
            'word': 'w',
            }
        ret = process_mongodb_ipa._process_document(document, True)
        self.assertEqual(
            ret,
            {'word': 'w',
             'IPA': ['fem'],
             'language': 'ba',
             }
        )
