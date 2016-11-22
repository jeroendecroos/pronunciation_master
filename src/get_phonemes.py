""" get_frequency_master gets the most frequent words for a language
"""
import argparse
import StringIO
import requests

import resources

def get_phonemes(language):
    return []

def _parse_arguments():
    """ parse the arguments from the commandline

    Arguments:
        None
    Returns:
        Namespace
    """
    parser = argparse.ArgumentParser(description='Get the phonemes from a language')
    parser.add_argument('--language', dest='language', required=True,
        help='the language we want the list for')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    phonemes = get_phonemes(args.language)
    print('\n'.join(phonemes[:5]))
