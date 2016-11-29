
import tests.testlib.testcase as testcase
import language_codes

class MapLanguageToHermitDaveCodeTest(testcase.BaseTestCase):
    def setUp(self):
        self.fun = language_codes._map_language_to_hermitdave_code

    def test_dutch(self):
        self.assertEqual(self.fun('dutch'), 'nl')

    def test_unknown_language(self):
        with self.assertRaises(ValueError):
            self.fun('unknownlanguages')

