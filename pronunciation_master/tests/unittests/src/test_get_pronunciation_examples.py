import unittest
import testing.postgresql
import psycopg2
from nose2.tools import params
import mock
import os

from pronunciation_master.tests.testlib import testcase, project_vars
from pronunciation_master.src import get_pronunciation_examples

available_phonemes = ['a', 'b', 'c']
PASSWORD = 'dog'


def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn(password="None"))
    cursor = conn.cursor()
    cursor.execute("ALTER USER postgres PASSWORD '{}'".format(PASSWORD))
    cursor.close()
    conn.commit()
    conn.close()


Postgresql = testing.postgresql.PostgresqlFactory(
    cache_initialized_db=True,
    on_initialized=handler)


def tearDownModule():
    Postgresql.clear_cache()


def _project_config():
    return os.path.join(project_vars.ASSETS_DIR, 'db_config.test.json')


class DataGettersTest(testcase.BaseTestCase):

    def data_getter(self):
        return get_pronunciation_examples.DataGetters('l')


@mock.patch('pronunciation_master.src.get_phonemes.get_phonemes')
class DataGettersTestGetPhonemes(DataGettersTest):
    def test_phonemes(self, mock_phonemes):
        mock_phonemes.return_value = ['a']
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.phonemes(),
            ['a']
            )

    def test_phonemes_called_twice(self, mock_phonemes):
        mock_phonemes.return_value = ['a']
        data_getter = self.data_getter()
        data_getter.phonemes(),
        self.assertItemsEqual(
            data_getter.phonemes(),
            ['a']
            )
        self.assertEqual(mock_phonemes.call_count, 1)


@mock.patch('pronunciation_master.src.get_frequent_words.get_frequency_list')
class DataGettersTestGetFrequencyList(DataGettersTest):
    def test_words(self, mock_frequency):
        mock_frequency.return_value = ['a']
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.words(),
            ['a']
            )


@mock.patch('pronunciation_master.src.get_pronunciations.get_pronunciations')
class DataGettersTestGetPronunciations(DataGettersTest):
    def test_pronunciations(self, mock_pronunciations):
        mock_pronunciations.return_value = [['a']]
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.pronunciations('w'),
            [['a']]
            )

    def test_pronunciations_no_return(self, mock_pronunciations):
        mock_pronunciations.return_value = None
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.IPA_pronunciations('w'),
            [],
            )


class DatabaseDataGettersTest(testcase.BaseTestCase):
    def data_getter(self):
        return get_pronunciation_examples.DatabaseDataGetters(
            'lang',
            _project_config())


@mock.patch('pronunciation_master.src.database.Table.get_data')
class DatabaseDataGettersTestGetData(DatabaseDataGettersTest):

    def test_phonemes(self, mock_phonemes):
        mock_phonemes.return_value = ['a']
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.phonemes(),
            ['a']
            )

    def test_phonemes_called_twice(self, mock_phonemes):
        mock_phonemes.return_value = ['a']
        data_getter = self.data_getter()
        data_getter.phonemes(),
        self.assertItemsEqual(
            data_getter.phonemes(),
            ['a']
            )
        self.assertEqual(mock_phonemes.call_count, 1)

    def test_words(self, mock_frequency):
        mock_frequency.return_value = ['a']
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.words(),
            ['a']
            )

    def test_pronunciations(self, mock_pronunciations):
        mock_pronunciations.return_value = [['a']]
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.pronunciations('w'),
            [['a']]
            )

    def test_IPA_pronunciations(self, mock_pronunciations):
        mock_pronunciations.return_value = ['a,b']
        data_getter = self.data_getter()
        self.assertItemsEqual(
            data_getter.IPA_pronunciations('w'),
            [['a', 'b']]
            )


@mock.patch('pronunciation_master.src.get_pronunciations.get_pronunciations')
class DatabaseDataGettersTestPronunciations(DatabaseDataGettersTest):
    def test_fallback(self, mock_pronunciations):
        mock_pronunciations.return_value = 5
        data_getter = self.data_getter()
        data_getter.fallback = True
        self.assertEqual(
            data_getter._try_fallback(None, 'pronunciations', args=['fa']),
            5,
            )

    def test_fallback_no_action(self, _):
        data_getter = self.data_getter()
        data_getter.fallback = True
        self.assertEqual(
            data_getter._try_fallback(5, 'pronunciations', fail=False),
            5,
            )

    def test_fallback_fail(self, mock_pronunciations):
        mock_pronunciations.return_value = None
        data_getter = self.data_getter()
        data_getter.fallback = True
        with self.assertRaises(RuntimeError):
            data_getter._try_fallback(
                None,
                'pronunciations',
                fail=True,
                args=['fa'],
                )


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
    @property
    def data_getters(self):
        return self._data_getters

    @data_getters.setter
    def data_getters(self, data_getter):
        self._data_getters = data_getter
        get_pronunciation_examples.DataGetters = self.data_getters
        get_pronunciation_examples.DatabaseDataGetters = self.data_getters

    def setUp(self):
        self._safe = get_pronunciation_examples.DataGetters
        self._safe2 = get_pronunciation_examples.DatabaseDataGetters
        self.data_getters = create_data_getter_fake(
            ['a', 'b'],
            ['a', 'b'],
            ['word'],
            )

    def tearDown(self):
        get_pronunciation_examples.DataGetters = self._safe
        get_pronunciation_examples.DatabaseDataGetters = self._safe2


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
        self.data_getters = create_data_getter_fake(
            ['a', 'b'],
            ['ab'],
            ['word'])
        examples = self.fun(
            'dutch',
            max_words=1)
        self.assertItemsEqual(examples.keys(), ['a', 'b'])
        self.assertItemsEqual(examples['a'], ['word'])

    def test_use_database(self):
        self.data_getters = create_data_getter_fake(
            ['a', 'b'],
            ['ab'],
            ['word'])
        examples = self.fun(
            'dutch',
            max_words=1,
            use_database='only',
            )
        self.assertItemsEqual(examples.keys(), ['a', 'b'])
        self.assertItemsEqual(examples['a'], ['word'])

    def test_no_word(self):
        self.data_getters._words = ['notinlist']
        examples = self.fun(
            'dutch',
            max_words=1)
        self.assertItemsEqual(examples['a'], [])

    def test_list_return_value(self):
        self.data_getters._words = ['notinlist']
        examples = self.fun(
            'dutch',
            list_return_value=True,
            max_words=1)
        self.assertItemsEqual(
            examples,
            [('a', []), ('b', [])],
            )

    def test_stop_when_minimum_examples_reached(self):
        self.data_getters = create_data_getter_fake(
            ['a'],
            ['a'],
            ['word', '1', '2'])
        self.data_getters.pronunciations = mock.Mock(return_value=['a'])
        examples = self.fun('dutch', max_words=3, minimum_examples=1)
        self.assertItemsEqual(examples['a'], ['word'])
        self.assertEqual(self.data_getters.pronunciations.call_count, 1)


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
        self.data_getters = create_data_getter_fake(
            ['a', "b"],
            ['ab'],
            ['word', 'boss'])
        examples = [x for x in self.fun(
            'dutch',
            data_getters_class=self.data_getters,
            max_words=1)]
        word = [x for x in examples if x.word == 'word'][0]
        self.assertEqual(word.IPA_pronunciation, ['a', 'b'])

    def test_no_pronunciations(self):
        self.data_getters.words = mock.Mock(return_value=['word', 'no_pron'])

        def pronunciations(y, x):
            return ['a'] if x == 'word' else []
        self.data_getters.pronunciations = pronunciations
        examples = list(self.fun(
            'dutch',
            data_getters_class=self.data_getters,
            ))
        example = [x for x in examples if x.word == 'no_pron']
        self.assertEqual(example, [])


def create_data_getter_fake(phonemes=None, pronunciations=None, words=None):
    class DataGetterFake(object):
        def __init__(self, language=None, *args, **kwargs):
            self._language = language

        def phonemes(self):
            return self._phonemes

        def pronunciations(self, word):
            return self._pronunciations

        def words(self):
            return self._words

        def IPA_pronunciations(self, word):
            IPA = getattr(
                self,
                '_IPA_pronunciations',
                [[c for c in x] for x in self.pronunciations(word)])
            return [get_pronunciation_examples.Pronunciation.from_IPA(i)
                    for i in IPA]

    DataGetterFake._pronunciations = pronunciations
    DataGetterFake._phonemes = phonemes
    DataGetterFake._words = words
    return DataGetterFake


class DataGetterIPAPronunciationTest(testcase.BaseTestCase):
    def test_create_good(self):
        data_getter = get_pronunciation_examples.DataGetters('')
        data_getter._phonemes = ['a']
        pronunciation = data_getter._create('aaa')
        expected_type = get_pronunciation_examples.Pronunciation
        self.assertTrue(isinstance(pronunciation.next(), expected_type))

    @params(
            ('one phoneme', ['a'], 1),
            ('two phonemes', ['ab'], 1),
            ('two pronounciations', ['a', 'b'], 2),
            ('one right, one wrong', ['a', 'x'], 1),
            ('one right, one partialy wrong', ['ab', 'ax'], 1),
            )
    def test_create_multiple(self, _, entry, number_created):
        data_getter = get_pronunciation_examples.DataGetters('')
        data_getter._phonemes = available_phonemes
        data_getter.pronunciations = mock.Mock(return_value=entry)
        IPAs = [x for x in data_getter.IPA_pronunciations('Word')]
        self.assertEqual(len(IPAs), number_created)


class PronunciationTest(testcase.BaseTestCase):
    def setUp(self):
        self.creator = get_pronunciation_examples.Pronunciation.from_original

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
