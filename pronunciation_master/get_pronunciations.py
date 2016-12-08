""" get_pronunciations gets the pronunciations for a word in a language
"""
import re
import argparse
import itertools

from wiktionaryparser import WiktionaryParser

import language_codes

def get_pronunciations(language, word):
    """ main function of module,
    gets the pronunciations for a 'word' in a 'language'
    dependency on Wiktionary (get_wiktionary_entry) to get this
    Arguments:
        language = language to get pronunciations for
        word = word to get the pronunciations for
    Returns:
        set of pronunciations set('pron1', 'pron2', ...)
    """
    language_code = language_codes.Wiktionary.map(language)
    wiktionary_entry = get_wiktionary_entry(language_code, word)
    pronunciation_entries = filter_pronunciations(wiktionary_entry)
    pronunciations = list_pronunciations(pronunciation_entries)
    return pronunciations

def get_wiktionary_entry(language, word):
    """Interface to the requestion something from wiktionary.
    Arguments:
        language = language of which we want the entry
        word = word  of which we want the entry
    Returns:
        parsed wiktionary page
    """
    parser = WiktionaryParser()
    parser.set_default_language(language)
    return parser.fetch(word)

def filter_pronunciations(wiktionary_entry):
    """ filters out only the pronunciation entries of a wikipedia page
    Arguments:
        wiktionary_entry = parsed wiktionary page
    Returns:
        iteratable of pronunciation entries : (entry1; entry2, ...)
    """
    key = 'pronunciations'
    pronunciation_entries = (entry.get(key, []) for entry in wiktionary_entry)
    pronunciations = itertools.chain.from_iterable(pronunciation_entries)
    return pronunciations

def list_pronunciations(pronunciation_entries):
    """ Parses all the pronunciations from the entries
    Arguments:
        pronunciation_entries = a iteratable of entries to parse
    Returns:
        set of pronunciations : set(pron1, pron2, ...)
    """
    pronunciations = set()
    for entry in pronunciation_entries:
        m = re.search('IPA: */(.*)/', entry)
        if m:
            pronunciations.add(m.group(1))
    return pronunciations

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

def main():
    args = _parse_arguments()
    pronunciations = get_pronunciations(args.language, args.word)
    if not pronunciations:
        message = "No pronunciations found for word '{}' in language '{}'"
        raise RuntimeError(message.format(word, language))
    for pronunciation in pronunciations:
        print(pronunciation)


if __name__ == '__main__':
    main()
