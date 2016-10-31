import unittest
import tempfile
import os

import tests.testlib.testcase as testcase
import get_frequency_list

class MapLanguageToHermitDaveCodeTest(testcase.BaseTestCase):
    def test_dutch(self):
        fun = get_frequency_list._map_language_to_hermitdave_code
        self.assertEqual(fun('dutch'), 'nl')

class GetFrequencyListFromFile(testcase.BaseTestCase):
    def test_word_freq_list(self):
        freq_list = [
            ('word1', 1),
            ('word2', 2),
            ('word3', 3),
            ('word4', 4),
            ('word5', 5),
            ('word6', 6),
            ('word7', 7),
            ('word8', 8),
            ('word9', 9),
            ('word10', 10),
                ]
        _, temp_filepath = tempfile.mkstemp()
        fun = get_frequency_list._get_frequency_list_from_file
        words = [word for word, freq in freq_list]
        try:
            with open(temp_filepath, 'w') as temp_stream:
                for word, freq in freq_list:
                    temp_stream.write('{}\t{}\n'.format(word, freq))
            freq_list_answer = fun(temp_filepath)
            self.assertEqual(freq_list_answer, words)
        finally:
            os.remove(temp_filepath)

class GetHermitdavePage(testcase.BaseTestCase):
    def test_dutch_first_line(self):
        page = get_frequency_list._get_hermitdave_page('nl')
        line = page.split('\n')[0]
        self.assertEqual(line, 'ik 8106228')

if __name__ == '__main__':
    unittest.main()

