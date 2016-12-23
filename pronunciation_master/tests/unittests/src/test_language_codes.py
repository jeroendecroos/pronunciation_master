from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import language_codes


class LanguageCodeTest(testcase.BaseTestCase):
    def setUp(self):
        self.fun = language_codes.LanguageCodes.map

    def test_for_unknown_language(self):
        with self.assertRaises(ValueError):
            self.fun('unknownlanguages')


class HermitDaveLanguageCodeTest(LanguageCodeTest):
    def setUp(self):
        self.fun = language_codes.HermitDave.map

    @params(('dutch', 'nl'),
            ('Dutch', 'nl'),
            ('aragonese', 'arg'),
            )
    def test_language(self, language, code):
        self.assertEqual(self.fun(language), code)


class PhoibeLanguageCodeTest(LanguageCodeTest):
    def setUp(self):
        self.fun = language_codes.Phoibe.map

    @params(('dutch', 'nld'),
            ('Dutch', 'nld'),
            ('aragonese', 'arg'),
            )
    def test_language(self, language, code):
        self.assertEqual(self.fun(language), code)
