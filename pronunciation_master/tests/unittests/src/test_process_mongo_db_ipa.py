import unittest

import mock
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import process_mongodb_ipa


class FilterPronunciationsTest(testcase.BaseTestCase):
    @params(
        ("ik",
            u'\n* {{rhymes|\u026ak|lang=nl}}\n* {{audio|Nl-ik.ogg|audio|lang=nl}}\n* {{IPA|/\u026ak/|lang=nl}} (stressed), {{IPA|/\u0259k/|lang=nl}} (unstressed)\n\n',
            [u'\u026ak', u'\u0259k']),
        ("femme",
            u'\n* {{IPA|/f\u025bm/|lang=en}}\n\n',
            [u'f\u025bm']),
        ("het",
            u'\n* {{rhymes|\u0259t|\u025bt|lang=nl}}\n* {{a|BE}} {{IPA|/\u0259t/|/\u0266\u0259t/|lang=nl}}\n* {{audio|Nl-het (Belgium).ogg|audio (Belgium)|lang=nl}}\n* {{a|NL}} {{IPA|lang=nl|/\u0259t/}} {{qualifier|usually}}, {{IPA|lang=nl|/\u0266\u025bt/}} {{qualifier|when stressed}}\n* {{audio|Nl-het.ogg|audio (Netherlands)|lang=nl}}\n\n',
            [u'\u0259t', u'\u0266\u0259t', u'\u0266\u025bt']),

        )
    def test_process_ipa(self, _, pronunciation_section, expected):
        result = process_mongodb_ipa.process_ipa(pronunciation_section)
        self.assertItemsEqual(result, set(expected))

