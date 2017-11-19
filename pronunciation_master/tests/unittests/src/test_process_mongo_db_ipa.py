import unittest

import mock
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import process_mongodb_ipa


class FilterPronunciationsTest(testcase.BaseTestCase):
    @params(
        ("ik",
            [u'\n* {{rhymes|\u026ak|lang=nl}}\n* {{audio|Nl-ik.ogg|audio|lang=nl}}\n* {{IPA|/\u026ak/|lang=nl}} (stressed), {{IPA|/\u0259k/|lang=nl}} (unstressed)\n\n'],
            ['\u026ak', '\u0259k']),
        )
    def test_process_ipa(self, _, pronunciation_section, expected):
        result = process_mongo_db_ipa.process_ipa(pronunciation_section)
        self.assertEqual(result, expected)

