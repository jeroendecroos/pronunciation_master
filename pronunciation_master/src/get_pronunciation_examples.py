""" get_pronunciation_examples gives the most frequent used words
    that have a certain phoneme in its pronunciation
"""
import functools

import commandline
import get_phonemes
import get_pronunciations
import get_frequent_words


def _all_have_same_length(items):
    example = next(iter(items))
    return all(len(item) == len(example) for item in items)


class DataGetters(object):
    """ datastructure to hold different functions to get data
    """
    phonemes = staticmethod(get_phonemes.get_phonemes)
    words = staticmethod(get_frequent_words.get_frequency_list)
    pronunciations = staticmethod(get_pronunciations.get_pronunciations)


class DatabaseDataGetters(DataGetters):
    """ gets data from database.
    """
    phonemes = staticmethod(get_phonemes.get_phonemes)
    words = staticmethod(get_frequent_words.get_frequency_list)
    pronunciations = staticmethod(get_pronunciations.get_pronunciations)


def _get_equal_phonemes(pronunciations):
    """ gets all phonemes that are equal for each pronunciation
        unequal lengths 'abc', 'bc' will be all ignored till better algorithm
    """
    example = next(iter(pronunciations))  # set robust
    equal_phonemes = [
        phoneme
        for i, phoneme in enumerate(example)
        if all(pronunciation[i] == phoneme for pronunciation in pronunciations)
    ]
    return set(equal_phonemes)


class PronunciationFactory(object):
    def __init__(self, data_getters, language):
        self.data_getters = data_getters
        self.phonemes = data_getters.phonemes(language)
        self.language = language

    def create_multiple_pronunciations(self, word):
        pronunciations = self.data_getters.pronunciations(self.language, word)
        if not pronunciations:
            return []
        return list(self._create(pronunciations))

    def _create(self, pronunciations):
        for pronunciation in pronunciations:
            try:
                yield Pronunciation(pronunciation, self.phonemes)
            except ValueError:
                continue


class Pronunciation(object):
    """ class to split up to hold pronunciations data
    """
    def __init__(self, pronunciation, phonemes):
        self._phonemes = sorted(phonemes, key=len, reverse=True)
        self.original_pronunciation = pronunciation
        self.IPA_pronunciation = self._split_into_phonemes(pronunciation)

    def __iter__(self):
        return iter(self.IPA_pronunciation)

    def __len__(self):
        return len(self.IPA_pronunciation)

    def __getitem__(self, index):
        return self.IPA_pronunciation[index]

    def _split_into_phonemes(self, pronunciation):
        pronunciation_splitted = []
        while pronunciation:
            phoneme = self._get_next_phoneme(pronunciation)
            if not phoneme:
                template = 'not all known phonemes in pronunciation {}+{}'
                raise ValueError(template.format(pronunciation_splitted,
                                                 pronunciation))
            pronunciation_splitted.append(phoneme)
            pronunciation = pronunciation[len(phoneme):]
        return pronunciation_splitted

    def _get_next_phoneme(self, pronunciation):
        for phoneme in self._phonemes:
            if pronunciation.startswith(phoneme):
                return phoneme
        return None


class PronunciationExamples(object):
    def __init__(self, phonemes, minimum_examples=0, maximum_examples=5):
        self._examples = {key: [] for key in phonemes}
        #self._factory = PronunciationFactory(phonemes)
        assert minimum_examples <= maximum_examples
        self.maximum_examples = maximum_examples
        self.minimum_examples = minimum_examples

    def add_pronunciations(self, word, pronunciations):
        """ adds for each phoneme in the pronunciations this words
        if there is ambiguety, the word is not added
                ('ab', 'ac'-> only phoneme 'a')
        unequal lengths 'abc', 'bc' will be all ignored till better algorithm
        """
        #pronunciations_IPA = self._factory.create_multiple(pronunciations)
        pronunciations_IPA = list(pronunciations)
        if pronunciations_IPA and _all_have_same_length(pronunciations_IPA):
            phonemes = _get_equal_phonemes(pronunciations_IPA)
            for phoneme in phonemes:
                if len(self._examples[phoneme]) < self.maximum_examples:
                    assert phoneme in self._examples
                    self._examples[phoneme].append(word)

    def reached_minimum(self):
        """ Check if all phonemes have at least the minimum amount of examples
        """
        if not self.minimum_examples:
            return False
        return all(len(v) >= self.minimum_examples
                   for v in self._examples.values())

    def __getitem__(self, name):
        return self._examples[name]

    def __iter__(self):
        return iter(self._examples)

    def keys(self):
        return self._examples.keys()

    def items(self):
        return self._examples.items()

    def values(self):
        return self._examples.values()


def get_pronunciation_examples(language, use_database="not", db_config=None, max_words=10, **kwargs):
    """ get the pronunciation examples for a certain language
    Arguments:
        Language = target language
        max_words = maximum number of words to try
    """
    if use_database != "not":
        raise NotImplementedError
    phonemes = DataGetters.phonemes(language)
    frequent_words = DataGetters.words(language)
    examples = PronunciationExamples(phonemes, **kwargs)
    factory = PronunciationFactory(DataGetters, language)
    for word in frequent_words[:max_words]:
        pronunciations = list(factory.create_multiple_pronunciations(word))
        if pronunciations:
            examples.add_pronunciations(word, pronunciations)
        if examples.reached_minimum():
            break
    return examples


def get_processed_ipas(language, data_getters=DataGetters, max_words=15):
    frequent_words = data_getters.words(language)
    factory = PronunciationFactory(data_getters, language)
    for i, word in enumerate(frequent_words):
        if max_words == i:
            break
        pronunciations = list(factory.create_multiple_pronunciations(word))
        for pronunciation in pronunciations:
            pronunciation.word = word
            yield pronunciation


def not_enough_examples_warnings(examples, minimum):
    warnings = []
    warning_template = u"Couldn't find enough examples ({}) for '{}'"
    for phoneme, words in examples.items():
        if len(words) < minimum:
            message = warning_template.format(minimum, phoneme)
            warnings.append(message)
    return warnings


if __name__ == '__main__':
    description = 'Get the pronunciaton_examples for a language'
    args = commandline.LanguageAndDatabaseInput.parse_arguments(
            description,
            extra_arguments=[
                'maximum_words_to_try',
                'minimum_examples',
                'maximum_examples'])
    pronunciation_examples = get_pronunciation_examples(
        args.language,
        db_config=args.db_config,
        use_database=args.use_database,
        max_words=args.maximum_words_to_try,
        maximum_examples=args.maximum_examples,
        minimum_examples=args.minimum_examples)
    not_reached_messages = not_enough_examples_warnings(
            pronunciation_examples, args.minimum_examples)
    commandline.output_warnings(not_reached_messages)
    commandline.output_dict(pronunciation_examples)
