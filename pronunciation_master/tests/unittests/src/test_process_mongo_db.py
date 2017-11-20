import unittest

import mock
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import process_mongodb_ipa


class FilterPronunciationsTest(testcase.BaseTestCase):
    def test_process_ipa(self, _, pronunciation_section, expected):

