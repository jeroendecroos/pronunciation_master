import unittest

import mock
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import get_pronunciations


class FilterPronunciationsTest(testcase.BaseTestCase):

    @params(
        ("no entry",
            [],
            []),
        ("one entry",
            [{'pronunciations': ['burp']}],
            ['burp']),
        ("one entry multiple pronunciations",
            [{'pronunciations': ['burp', 'burp2']}],
            ['burp', 'burp2']),
        ("one entry no pronunciations",
            [{'a': 'b'}],
            []),
        ("multiple entries",
            [{'pronunciations': ['burp1']},
                {'pronunciations': ['burp2']}],
            ['burp1', 'burp2']),
        )
    def test_floor(self, name, entry, expected):
        fun = get_pronunciations.filter_pronunciations
        self.assertItemsEqual(fun(entry), expected)


class ListPronunciationsTest(testcase.BaseTestCase):

    @params(
        ("no entry",
            [],
            []),
        ("one IPA",
            ['IPA: /ba/'],
            ['ba']),
        ("two IPA",
            ['IPA: /ba1/', 'IPA: /ba2/'],
            ['ba1', 'ba2']),
        ("two equal IPA",
            ['IPA: /ba1/', 'IPA: /ba1/'],
            ['ba1']),
        ("one IPA, one garbage",
            ['IPA: /ba1/', 'Rhymes: /ba2/'],
            ['ba1']),
        ("two IPA in one entry",
            ['IPA: /ba1/ IPA: /ba2/'],
            ['ba1', 'ba2']),
            )
    def test_floor(self, name, entry, expected):
        fun = get_pronunciations.list_pronunciations
        self.assertItemsEqual(fun(entry), expected)


class GetPronunciationsTest(testcase.BaseTestCase):
    def setUp(self):
        """ We need to fake get_wiktionary_entry because this makes an external call.
        """
        self.get_wiktionary_entry = mock.Mock()
        self.get_wiktionary_entry_bu = get_pronunciations.get_wiktionary_entry
        get_pronunciations.get_wiktionary_entry = self.get_wiktionary_entry
        self.fun = get_pronunciations.get_pronunciations
        self.get_wiktionary_entry.return_value = []

    def tearDown(self):
        get_pronunciations.get_wiktionary_entry = self.get_wiktionary_entry_bu

    def test_raise_bad_language(self):
        with self.assertRaises(ValueError):
            self.fun('unknown language', 'ba')

    def test_one_pronoun_on_wiktionary(self):
        entry = {'pronunciations': ['IPA: /ba/']}
        self.get_wiktionary_entry.return_value = [entry]
        ret = self.fun('dutch', 'bad')
        self.assertItemsEqual(ret, ['ba'])


class GetWiktionaryEntry(testcase.BaseTestCase):
    def test_interface(self):
        get_pronunciations.WiktionaryParser = mock.Mock()
        get_pronunciations.get_wiktionary_entry('lan', 'word')


if __name__ == '__main__':
    unittest.main()
