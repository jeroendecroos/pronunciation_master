""" get_frequency_master gets the most frequent words for a language
"""
import StringIO
import requests

import resources
import language_codes
import commandline


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
    hermitdave_language_code = language_codes.HermitDave.map(language)
    file_pointer = _get_hermitdave_page(hermitdave_language_code)
    return _get_frequency_list_from_filestream(file_pointer)


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

if __name__ == '__main__':
    args = commandline.LanguageInput.get_arguments('Get the word frequencies for a language')
    frequency_list = get_frequency_list(args.language)
    print('\n'.join(frequency_list[:5]))
