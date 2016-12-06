import os
import unittest
import tempfile

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
        self.assertItemsEqual(list(fun(entry)), expected)


class ListPronunciationsTest(testcase.BaseTestCase):

    @params(
        ("no entry",
            [],
            []
        ),
        ("one IPA",
            ['IPA: /tbat/'],
            ['ba']
        ),
        ("two IPA",
            ['IPA: /tba1st/', 'IPA: /tba2t/'],
            ['ba1', 'ba2']
        ),
        ("two equal IPA",
            ['IPA: /tba1st/', 'IPA: /tba1t/'],
            ['ba1']
        ),
        ("one IPA, one garbage",
            ['IPA: /tba1st/', 'Rhymes: /tba2t/'],
            ['ba1']
        ),
        )
    def test_floor(self, name, entry, expected):
        fun = get_pronunciations.list_pronunciations
        self.assertItemsEqual(list(fun(entry)), expected)

if __name__ == '__main__':
    unittest.main()

