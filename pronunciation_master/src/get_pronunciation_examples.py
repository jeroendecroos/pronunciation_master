""" get_pronunciation_examples gives the most frequent used words
    that have a certain phoneme in its pronunciation
"""

import commandline
import get_phonemes
import get_pronunciations
import get_frequent_words


def _all_have_same_length(items):
    example = next(iter(items))
    return all(len(item) == len(example) for item in items)


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
    def __init__(self, phonemes):
        self.phonemes = phonemes

    def create(self, pronunciation):
        return Pronunciation(pronunciation, self.phonemes)


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
    def __init__(self, phonemes, max_examples=5):
        self._examples = {key: [] for key in phonemes}
        self._factory = PronunciationFactory(phonemes)
        self.max_examples = max_examples

    def add_pronunciations(self, word, pronunciations):
        """ adds for each phoneme in the pronunciations this words
        if there is ambiguety, the word is not added
                ('ab', 'ac'-> only phoneme 'a')
        unequal lengths 'abc', 'bc' will be all ignored till better algorithm
        """
        pronunciations_IPA = list(self._IPA_pronunciations(pronunciations))
        if pronunciations_IPA and _all_have_same_length(pronunciations_IPA):
            phonemes = _get_equal_phonemes(pronunciations_IPA)
            for phoneme in phonemes:
                if len(self._examples[phoneme]) < self.max_examples:
                    self._examples[phoneme].append(word)

    def _IPA_pronunciations(self, pronunciations):
        for p in pronunciations:
            try:
                yield self._factory.create(p)
            except ValueError:
                continue

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


class DataGetters(object):
    """ datastructure to hold different functions to get data
    """
    phonemes = staticmethod(get_phonemes.get_phonemes)
    words = staticmethod(get_frequent_words.get_frequency_list)
    pronunciations = staticmethod(get_pronunciations.get_pronunciations)


def get_pronunciation_examples(language, max_words=1000):
    """ get the pronunciation examples for a certain language
    Arguments:
        Language = target language
        max_words = maximum number of words to try
    """
    phonemes = DataGetters.phonemes(language)
    frequent_words = DataGetters.words(language)
    examples = PronunciationExamples(phonemes)
    for word in frequent_words[:max_words]:
        pronunciations = DataGetters.pronunciations(language, word)
        if pronunciations:
            examples.add_pronunciations(word, pronunciations)
    return examples


if __name__ == '__main__':
    description = 'Get the pronunciaton_examples for a language'
    args = commandline.LanguageInput.parse_arguments(description)
    pronunciation_examples = get_pronunciation_examples(args.language)
    commandline.output_dict(pronunciation_examples)
