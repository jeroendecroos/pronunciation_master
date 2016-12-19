import unittest
import tempfile
import os

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import get_frequent_words


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
        fun = get_frequent_words._get_frequency_list_from_file
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
        page = get_frequent_words._get_hermitdave_page('nl')
        line = page.readline()
        self.assertEqual(line, 'ik 8106228\n')


if __name__ == '__main__':
    unittest.main()
