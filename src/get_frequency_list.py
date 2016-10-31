""" get_frequency_master gets the most frequent words for a language
"""
import argparse
import StringIO
import requests

import resources

def get_frequency_list(language):
    """ returns a list of the most frequent words of a language

    Arguments:
        language=String     language for which to get the list
    Returns
        List        most frequent words in frequency-order
    """
    return _get_frequency_list_from_hermitdave(language)

def _get_frequency_list_from_hermitdave(language):
    """ returns a list of the most frequent words of a language
    the frequency lists are processede starting from the list hermitdave made
    see: https://github.com/hermitdave/FrequencyWords/
    or https://invokeit.wordpress.com/frequency-word-lists/

    Arguments:
        language=String     language for which to get the list
    Returns
        List        most frequent words in frequency-order
    """
    hermitdave_language_code = _map_language_to_hermitdave_code(language)
    file_pointer = _get_hermitdave_page(hermitdave_language_code)
    return _get_frequency_list_from_filestream(file_pointer)


def _map_language_to_hermitdave_code(language):
    """ hermitdave probably uses ISO 639:1
    for the moment not doing anything smart
    Returns code for hermitdave
    """
    language = language.lower()
    codes = {'dutch':'nl'}
    if language not in codes:
        raise ValueError("Language '{}' is not known".format(language))
    return codes[language]

def _get_hermitdave_page(language_code):
    """ get the page from hermitdave's github
    Arguments are the language_code to hermitdave_page
    Returns: stream
    """
    page_name = '{}_50k.txt'.format(language_code)
    page_path = '/'.join([
        resources.hermit_dave_github,
        language_code,
        page_name])
    text = requests.get(page_path).text
    stream = StringIO.StringIO(text)
    return stream

def _get_frequency_list_from_file(file_pointer):
    """Take a pointer to a file and get the frequency list from it
    """
    with open(file_pointer) as instream:
        freq_list = _get_frequency_list_from_filestream(instream)
    return freq_list

def _get_frequency_list_from_filestream(instream):
    """Take a file stream and get the frequency list from it
    """
    freq_list = []
    for line in instream:
        if not line:
            break
        word, freq = line.split()
        freq_list.append(word)
    return freq_list

def _parse_arguments():
    """ parse the arguments from the commandline

    Arguments:
        None
    Returns:
        Namespace
    """
    parser = argparse.ArgumentParser(description='Get the word frequencies for a language')
    parser.add_argument('--language', dest='language', required=True,
        help='the language we want the list for')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    frequency_list = get_frequency_list(args.language)
    print('\n'.join(frequency_list[:5]))
