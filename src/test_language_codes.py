
import tests.testlib.testcase as testcase
import language_codes

class HermitDaveLanguageCodeTest(testcase.BaseTestCase):
    def setUp(self):
        self.fun = language_codes.HermitDave.map

    def test_dutch(self):
        self.assertEqual(self.fun('dutch'), 'nl')

    def test_unknown_language(self):
        with self.assertRaises(ValueError):
            self.fun('unknownlanguages')

