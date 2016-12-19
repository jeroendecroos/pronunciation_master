import unittest
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import get_pronunciation_examples

available_phonemes = ['a', 'b', 'c']


class PronunciationExamplesTest(testcase.BaseTestCase):
    def setUp(self):
        self.test_class = get_pronunciation_examples.PronunciationExamples

    def test__init__(self):
        self.test_class(['a'])

    def test_keys(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.keys(), 'a')

    def test_items(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.items(), [('a', [])])

    def test_values(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.values(), [[]])

    @params(
        ('non valid phonemes',
            ('one', ['g']),
            {'a': [], 'b': [], 'c': []}),
        ('1 pronunciation, 1phoneme',
            ('one', ['a']),
            {'a': ['one'], 'b': [], 'c': []}),
        ('1 pronunciation, 2phoneme',
            ('one', ['ab']),
            {'a': ['one'], 'b': ['one'], 'c': []}),
        ('2 pronunciation, unequal length',
            ('one', ['a', 'ab']),
            {'a': [], 'b': [], 'c': []}),
        ('2 pronunciation, different phonemes',
            ('one', ['a', 'b']),
            {'a': [], 'b': [], 'c': []}),
        ('2 pronunciation, 1 common phoneme',
            ('one', ['ac', 'bc']),
            {'a': [], 'b': [], 'c': ['one']})
        )
    def test_add_once_pronunciations(self, _, entry, expected):
        examples = self.test_class(available_phonemes)
        examples.add_pronunciations(*entry)
        self.assertDictEqual(dict(examples), expected)

    @params(
            ('one phoneme', ['a']),
            ('two phonemes', ['ab']),
            ('two pronounciations', ['a', 'b']),
            )
    def test_all_valid_phonemes_positive(self, _, entry):
        examples = self.test_class(available_phonemes)
        self.assertTrue(examples._all_valid_phonemes(entry))

    @params(
            ('one right, one wrong', ['a', 'x']),
            ('one right, one partialy wrong', ['ab', 'ax']),
            )
    def test_all_valid_phonemes_negative(self, _, entry):
        examples = self.test_class(available_phonemes)
        self.assertFalse(examples._all_valid_phonemes(entry))


class AllHaveSameLengthTest(testcase.BaseTestCase):
    def setUp(self):
        self.fun = get_pronunciation_examples._all_have_same_length

    @params(('one empty', ['']),
            ('one', ['a']),
            ('two equal', ['a', 'b']),
            ('three equal', ['a', 'b', 'c']),
            )
    def test_positive_case(self, _, entry):
        self.assertTrue(self.fun(entry))

    @params(('two unequal', ['ab', 'b']),
            ('two equal, one different', ['aa', 'b', 'c']),
            )
    def test_negative_case(self, _, entry):
        self.assertFalse(self.fun(entry))


class GetEqualPhonemesTest(testcase.BaseTestCase):
    def setUp(self):
        self.fun = get_pronunciation_examples._get_equal_phonemes

    @params(
        ('one entry one phoneme',
            ['a'], ['a']),
        ('one entry two phonemes',
            ['ab'], ['a', 'b']),
        ('one entry equal phonemes',
            ['aa'], ['a']),
        ('two entries unequal phonemes',
            ['a', 'b'], []),
        ('two entries partly equal phonemes',
            ['ab', 'ab'], ['a', 'b']),
        ('two entries symmetric equal phonemes',
            ['ab', 'ba'], []),
        ('three entries two equal, other different',
            ['ab', 'ac', 'dd'], []),
        ('three entries two equal, other partially different',
            ['ab', 'ab', 'ad'], ['a']),
            )
    def test_positive_case(self, _, entry, expected):
        self.assertItemsEqual(self.fun(entry), expected)


if __name__ == '__main__':
    unittest.main()
