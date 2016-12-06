""" get_pronunciation_examples gives the most frequent used words that have a certain phoneme in its pronunciation
"""
import argparse

import language_codes

def get_pronunciation_examples(language):
    pass

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
