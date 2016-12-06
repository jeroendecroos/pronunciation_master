""" get_pronunciations gets the pronunciations for a word in a language
"""
import argparse
import itertools

from wiktionaryparser import WiktionaryParser


def get_pronunciations(language, word):
    wiktionary_entry = get_wiktionary_entry(language, word)
    pronunciation_entries = filter_pronunciations(wiktionary_entry)
    pronunciations = list_pronunciations(pronunciation_entries)
    return pronunciations

def get_wiktionary_entry(language, word):
    parser = WiktionaryParser()
    parser.set_default_language(language)
    return parser.fetch(word)

def filter_pronunciations(wiktionary_entry):
    key = 'pronunciations'
    pronunciation_entries = (entry.get(key, []) for entry in wiktionary_entry)
    pronunciations = itertools.chain.from_iterable(pronunciation_entries)
    return pronunciations

def list_pronunciations(pronunciation_entries):
    pass

def _parse_arguments():
    """ parse the arguments from the commandline

    Arguments:
        None
    Returns:
        Namespace
"""
    parser = argparse.ArgumentParser(description='Get the phonemes from a language') 
    parser.add_argument('--language', dest='language', required=True,
        help='the language we want the pronuncations for')
    parser.add_argument('--word', dest='word', required=True,
        help='the word we want the pronunciations for')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    pronunciations = get_pronunciations(args.language, args.world)
    for pronunciation in pronunciations:
        print(pronunciation)
