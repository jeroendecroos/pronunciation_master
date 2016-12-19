
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

    def test_dutch(self):
        self.assertEqual(self.fun('dutch'), 'nl')


class PhoibeLanguageCodeTest(LanguageCodeTest):
    def setUp(self):
        self.fun = language_codes.Phoibe.map

    def test_dutch(self):
        self.assertEqual(self.fun('dutch'), 'nld')
