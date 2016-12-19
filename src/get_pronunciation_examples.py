""" get_pronunciation_examples gives the most frequent used words
    that have a certain phoneme in its pronunciation
"""

import commandline
import get_phonemes
import get_pronunciations
import get_frequent_words


def _all_have_same_length(items):
    example = next(iter(items))  # set robust
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


class PronunciationExamples(object):
    def __init__(self, phonemes):
        self._examples = {key: [] for key in phonemes}

    def add_pronunciations(self, word, pronunciations):
        """ adds for each phoneme in the pronunciations this words
        if there is ambiguety, the word is not added
                ('ab', 'ac'-> only phoneme 'a')
        unequal lengths 'abc', 'bc' will be all ignored till better algorithm
        """
        if _all_have_same_length(pronunciations):
            if self._all_valid_phonemes(pronunciations):
                phonemes = _get_equal_phonemes(pronunciations)
                [self._examples[phoneme].append(word) for phoneme in phonemes]

    def _all_valid_phonemes(self, pronunciations):
        return all(phoneme in self._examples
                   for pronunciation in pronunciations
                   for phoneme in pronunciation)

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


def get_pronunciation_examples(language, max=10):
    phonemes = get_phonemes.get_phonemes(language)
    frequent_words = get_frequent_words.get_frequency_list(language)
    examples = PronunciationExamples(phonemes)
    for word in frequent_words[:max]:
        pronunciations = get_pronunciations.get_pronunciations(language, word)
        if pronunciations:
            examples.add_pronunciations(word, pronunciations)
    return examples


if __name__ == '__main__':
    description = 'Get the pronunciaton_examples for a language'
    args = commandline.LanguageInput.parse_arguments(description)
    pronunciation_examples = get_pronunciation_examples(args.language)
    commandline.output_dict(pronunciation_examples)
