import unittest
from nose2.tools import params
import mock

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
        self.assertItemsEqual(examples.keys(), ['a'])

    def test_items(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.items(), [('a', [])])

    def test_values(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual(examples.values(), [[]])

    def test_iter(self):
        examples = self.test_class(['a'])
        self.assertItemsEqual([x for x in examples], ['a'])

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
            ('less', [('1', 'a')], 1),
            ('equal', [('1', 'a'), ('2', 'a')], 2),
            ('more', [('1', 'a'), ('2', 'a'), ('3', 'a')], 2),
            )
    def test_max_examples(self, _, entry, number_created):
        examples = self.test_class(available_phonemes, maximum_examples=2)
        for word, pronunciation in entry:
            examples.add_pronunciations(word, [pronunciation])
        self.assertEqual(len(examples['a']), number_created)

    @params(
            ('less', [('1', 'a')], False),
            ('equal', [('1', 'a'), ('2', 'a')], True),
            ('more', [('1', 'a'), ('2', 'a'), ('3', 'a')], True),
            ('one yes, one no', [('1', 'a'), ('2', 'a'), ('3', 'b')], False),
            )
    def test_reached_minimum(self, _, entry, reached):
        phonemes = set(e[1] for e in entry)
        examples = self.test_class(phonemes, minimum_examples=2)
        for word, pronunciation in entry:
            examples.add_pronunciations(word, [pronunciation])
        self.assertEqual(examples.reached_minimum(), reached)


class CheckExamplesNotReachingMinimumTest(testcase.BaseTestCase):
    def setUp(self):
        self.fun = get_pronunciation_examples.not_enough_examples_warnings

    def test_no_minimum(self):
        ret = self.fun({}, 0)
        self.assertFalse(ret)

    def test_success(self):
        ret = self.fun({'a': [1]}, 1)
        self.assertFalse(ret)

    def test_failure(self):
        ret = self.fun({'a': [1]}, 4)
        self.assertTrue(ret)


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


class FakeDataGettersTest(testcase.BaseTestCase):
    def setUp(self):
        data = mock.Mock()
        get_pronunciation_examples.DataGetters = data
        data.phonemes = mock.Mock(return_value=['a', 'b'])
        data.words = mock.Mock(return_value=['word'])
        data.pronunciations = mock.Mock(side_effect=self.get_pronunciations)
        self.data = data

class GetPronunciationExamplesTest(FakeDataGettersTest):
    def setUp(self):
        super(GetPronunciationExamplesTest, self).setUp()
        self.fun = get_pronunciation_examples.get_pronunciation_examples

    @staticmethod
    def get_pronunciations(x, y):
        pronunciations = {'word': ['a']}
        if y in pronunciations:
            return pronunciations[y]
        else:
            return []

    def test_one_word(self):
        examples = self.fun('dutch', 1)
        self.assertItemsEqual(examples.keys(), ['a', 'b'])
        self.assertItemsEqual(examples['a'], ['word'])

    def test_no_word(self):
        self.data.words = mock.Mock(return_value=['notinlist'])
        examples = self.fun('dutch', 1)
        self.assertItemsEqual(examples['a'], [])

    def test_stop_when_minimum_examples_reached(self):
        self.data.phonemes = mock.Mock(return_value=['a'])
        self.data.words = mock.Mock(return_value=['word', '1', '2'])
        examples = self.fun('dutch', 3, minimum_examples=1)
        self.assertItemsEqual(examples['a'], ['word'])
        self.assertEqual(self.data.pronunciations.call_count, 1)


class GetProcessedIpas(FakeDataGettersTest):
    @staticmethod
    def get_pronunciations(x, y):
        pronunciations = {'word': ['ab']}
        if y in pronunciations:
            return pronunciations[y]
        else:
            return []

    def setUp(self):
        super(GetProcessedIpas, self).setUp()
        self.fun = get_pronunciation_examples.get_processed_ipas

    def test_one_word(self):
        examples = [x for x in self.fun('dutch', 1)]
        word = [x for x in examples if x.word == 'word'][0]
        self.assertEqual(word.IPA_pronunciation, ['a', 'b'])

    def test_no_pronunciations(self):
        self.data.words = mock.Mock(return_value=['word', 'no_pron'])
        examples = [x for x in self.fun('dutch')]
        example =  [x for x in examples if x.word == 'no_pron']
        self.assertEqual(example, [])


class PronunciationFactoryTest(testcase.BaseTestCase):
    def test_create_good(self):
        factory = get_pronunciation_examples.PronunciationFactory(['a'])
        pronunciation = factory.create('aaa')
        expected_type = get_pronunciation_examples.Pronunciation
        self.assertTrue(isinstance(pronunciation, expected_type))

    def test_assert_raises_bad(self):
        factory = get_pronunciation_examples.PronunciationFactory(['a'])
        with self.assertRaises(ValueError):
            factory.create('bbb')

    @params(
            ('one phoneme', ['a'], 1),
            ('two phonemes', ['ab'], 1),
            ('two pronounciations', ['a', 'b'], 2),
            ('one right, one wrong', ['a', 'x'], 1),
            ('one right, one partialy wrong', ['ab', 'ax'], 1),
            )
    def test_create_multiple(self, _, entry, number_created):
        test_factory = get_pronunciation_examples.PronunciationFactory
        factory = test_factory(available_phonemes)
        IPAs = [x for x in factory.create_multiple(entry)]
        self.assertEqual(len(IPAs), number_created)


class PronunciationTest(testcase.BaseTestCase):
    def setUp(self):
        self.creator = get_pronunciation_examples.Pronunciation

    @params(('one phoneme', 'a', ['a']),
            ('two equal phonemes', 'aa', ['a', 'a']),
            ('two unequal phonemes', 'ab', ['a', 'b']),
            )
    def test_create_good_simple(self, _, entry, expected):
        pronunciation = self.creator(entry, ['a', 'b'])
        self.assertEqual(list(pronunciation), expected)

    @params(('one phoneme', 'ab', ['ab']),
            ('two equal phonemes', 'abab', ['ab', 'ab']),
            ('two unequal phonemes', 'abc', ['ab', 'c']),
            )
    def test_create_good_double_phonemes(self, _, entry, expected):
        pronunciation = self.creator(entry, ['ab', 'c'])
        self.assertEqual(list(pronunciation), expected)

    @params(('one bad', 'aX'),
            ('two bad', 'aXY'),
            ('one bad, one good', 'abX'),
            ('in between', 'aXb'),
            ('mixed', 'abaab'),
            )
    def test_assert_raises(self, _, entry):
        with self.assertRaises(ValueError):
            self.creator(entry, ['ab', 'c'])

    @params(('one phoneme', 'ab', ['ab']),
            ('two equal phonemes', 'abab', ['ab', 'ab']),
            ('two unequal phonemes', 'aba', ['ab', 'a']),
            ('two unequal phonemes', 'aab', ['a', 'ab']),
            )
    def test_create_good_overlap(self, _, entry, expected):
        pronunciation = self.creator(entry, ['ab', 'a'])
        self.assertEqual(list(pronunciation), expected)

    @params(('two bad', 'aXY'),
            ('one bad, one good', 'bab'),
            )
    def test_assert_raises_bad_overlap(self, _, entry):
        with self.assertRaises(ValueError):
            self.creator(entry, ['ab', 'a'])

    @params(('one phoneme', 'ab', ['ab']),
            ('two equal phonemes', 'abac', ['ab', 'ac']),
            )
    def test_create_good_partial_overlap(self, _, entry, expected):
        pronunciation = self.creator(entry, ['ab', 'ac'])
        self.assertEqual(list(pronunciation), expected)

    @params(('one phoneme', 'a', ['a']),
            ('two equal phonemes', 'aa', ['aa']),
            ('two equal phonemes', 'aab', ['aa', 'b']),
            ('two equal phonemes', 'aaa', ['aa', 'a']),
            )
    def test_create_good_short_long_version(self, _, entry, expected):
        pronunciation = self.creator(entry, ['a', 'aa', 'b'])
        self.assertEqual(list(pronunciation), expected)

    @params(('one phoneme', 'a', ['a']),
            ('two equal phonemes', 'ab', ['ab']),
            ('two equal phonemes', 'aab', ['a', 'ab']),
            ('two equal phonemes', 'abba', ['ab', 'b', 'a']),
            )
    def test_create_good_similar_splitted(self, _, entry, expected):
        pronunciation = self.creator(entry, ['a', 'ab', 'b'])
        self.assertEqual(list(pronunciation), expected)


if __name__ == '__main__':
    unittest.main()
