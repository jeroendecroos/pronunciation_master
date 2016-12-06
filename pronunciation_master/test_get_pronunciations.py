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
        self.assertEqual(list(fun(entry)), expected)

if __name__ == '__main__':
    unittest.main()

