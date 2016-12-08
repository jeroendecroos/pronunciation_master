import os
import unittest
import tempfile

import mock
from nose2.tools import params

import tests.testlib.testcase as testcase
import get_pronunciations

class FilterPronunciationsTest(testcase.BaseTestCase):

    @params(
        ("no entry",
            [],
            []
        ),
        ("one entry",
            [{'pronunciations':['burp']}],
            ['burp']
        ),
        ("one entry multiple pronunciations",
            [{'pronunciations':['burp', 'burp2']}],
            ['burp', 'burp2']
        ),
        ("one entry no pronunciations",
            [{'a':'b'}],
            []
        ),
        ("multiple entries",
            [{'pronunciations': ['burp1']},
                {'pronunciations': ['burp2']}],
            ['burp1', 'burp2']
            ),
        )
    def test_floor(self, name, entry, expected):
        fun = get_pronunciations.filter_pronunciations
        self.assertItemsEqual(fun(entry), expected)


class ListPronunciationsTest(testcase.BaseTestCase):

    @params(
        ("no entry",
            [],
            []
        ),
        ("one IPA",
            ['IPA: /ba/'],
            ['ba']
        ),
        ("two IPA",
            ['IPA: /ba1/', 'IPA: /ba2/'],
            ['ba1', 'ba2']
        ),
        ("two equal IPA",
            ['IPA: /ba1/', 'IPA: /ba1/'],
            ['ba1']
        ),
        ("one IPA, one garbage",
            ['IPA: /ba1/', 'Rhymes: /ba2/'],
            ['ba1']
        ),
        )
    def test_floor(self, name, entry, expected):
        fun = get_pronunciations.list_pronunciations
        self.assertItemsEqual(fun(entry), expected)

class GetPronunciationsTest(testcase.BaseTestCase):
    def setUp(self):
        """ We need to fake get_wiktionary_entry because this makes an external call.
        """
        self.get_wiktionary_entry = mock.Mock()
        get_pronunciations.get_wiktionary_entry = self.get_wiktionary_entry
        self.fun = get_pronunciations.get_pronunciations
        self.get_wiktionary_entry.return_value = []

    def test_raise_bad_language(self):
        with self.assertRaises(ValueError):
            self.fun('unknown language', 'ba')

    def test_one_pronoun_on_wiktionary(self):
        self.get_wiktionary_entry.return_value = [{'pronunciations':['IPA: /ba/']}]
        ret = self.fun('dutch', 'bad')
        self.assertItemsEqual(ret, ['ba'])

if __name__ == '__main__':
    unittest.main()

