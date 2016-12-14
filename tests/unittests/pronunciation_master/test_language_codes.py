
import tests.testlib.testcase as testcase
import pronunciation_master.language_codes as language_codes

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

