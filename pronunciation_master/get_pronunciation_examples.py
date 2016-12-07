""" get_pronunciation_examples gives the most frequent used words that have a certain phoneme in its pronunciation
"""
import argparse

import get_phonemes
import get_pronunciations
import get_frequent_words


class PronunciationExamples(object):
    def __init__(self, phonemes):
        self._examples = {key: [] for key in phonemes}

    def add_pronunciations(self, word, pronunciations):
        pass
    
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

def get_pronunciation_examples(language):
    phonemes = get_phonemes.get_phonemes(language)
    frequent_words = get_frequent_words.get_frequency_list(language)
    examples = PronunciationExamples(phonemes)
    for word in frequent_words:
        pronunciations = get_pronunciations.get_pronunciations(language, word)
        if pronunciations:
            examples.add_pronunciations(word, pronunciations)
    return examples

def _parse_arguments():
    """ parse the arguments from the commandline

    Arguments:
        None
    Returns:
        Namespace
    """
    parser = argparse.ArgumentParser(description='Get the pronunciaton_examples for a language')
    parser.add_argument('--language', dest='language', required=True,
        help='the language we want the examples for')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    pronunciation_examples = get_pronunciation_examples(args.language)
    for phoneme, examples in pronunciation_examples:
        print('{}: {}'.format(phoneme, examples))
