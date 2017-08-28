import mock
import os
import StringIO
import tempfile
import unittest

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import get_frequent_words


class GetFrequencyListFromFile(testcase.BaseTestCase):
    def setUp(self):
        _, self.temp_filepath = tempfile.mkstemp()
        self.fun = get_frequent_words._get_frequency_list_from_filestream

    def tearDown(self):
        os.remove(self.temp_filepath)


    def _create_freq_list(self):
        self.freq_list = [
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
        self.words = [word for word, freq in self.freq_list]
        with open(self.temp_filepath, 'w') as temp_stream:
            for word, freq in self.freq_list:
                temp_stream.write('{}\t{}\n'.format(word, freq))

    def test_word_freq_list_extended(self):
        self._create_freq_list()
        with open(self.temp_filepath) as instream:
            freq_list_answer = self.fun(instream, True)
        ranked_list = [(word, i+1, freq) for i, (word, freq) in enumerate(self.freq_list)]
        self.assertEqual(freq_list_answer, ranked_list)

    def test_word_freq_list(self):
        self._create_freq_list()
        with open(self.temp_filepath) as instream:
            freq_list_answer = self.fun(instream)
        self.assertEqual(freq_list_answer, self.words)

    def test_empty_line_file(self):
        with open(self.temp_filepath, 'w') as temp_stream:
            temp_stream.write('\n')
        with self.assertRaises(RuntimeError):
            with open(self.temp_filepath) as instream:
                self.fun(instream)


class GetHermitdavePage(testcase.BaseTestCase):
    def test_dutch_first_line(self):
        page = get_frequent_words._get_hermitdave_page('nl')
        line = page.readline()
        self.assertEqual(line, 'ik 8106228\n')


class GetFrequencyList(testcase.BaseTestCase):
    def setUp(self):
        self.fun = get_frequent_words.get_frequency_list

    def test_one_word(self):
        data = mock.Mock()
        get_frequent_words.FrequencySources = data
        data.language_code = mock.Mock(side_effect=lambda x: x)
        data.frequency_filestream = mock.Mock(return_value=StringIO.StringIO('word 5\n'))
        self.assertEqual(self.fun('dutch'), ['word'])


if __name__ == '__main__':
    unittest.main()
