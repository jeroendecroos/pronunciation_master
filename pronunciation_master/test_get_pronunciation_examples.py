import unittest
from nose2.tools import params

import tests.testlib.testcase as testcase
import get_pronunciation_examples

available_phonemes = ['a','b','c']

class PronunciationExamplesTest(testcase.BaseTestCase):
    def setUp(self):
        self.test_class = get_pronunciation_examples.PronunciationExamples

    def test__init__(self):
        examples = self.test_class(['a'])

    def test_keys(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.keys(), 'a')

    def test_items(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.items(), ('a', []))

    def test_values(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.items(), [[]])

    @params(
            ('1 pronunciation, 1phoneme',
                ('one', ['a']),
                {'a':['one'], 'b':[], 'c':[]}
            ),
            ('1 pronunciation, 2phoneme',
                ('one', ['ab']),
                {'a':['one'], 'b':['one'], 'c':[]}
            ),
            ('2 pronunciation, different phonemes',
                ('one', ['a', 'b']),
                {'a':[], 'b':[], 'c':[]}
            ),
            ('2 pronunciation, 1 common phoneme',
                ('one', ['ac', 'bc']),
                {'a':[], 'b':[], 'c':['one']}
            ))
    def test_add_once_pronunciations(self, name, entry, expected ):
        examples = self.test_class(available_phonemes)
        examples.add_pronunciations(*entry)
        self.assertItemsEqual(examples.items(), expected)



if __name__ == '__main__':
    unittest.main()

