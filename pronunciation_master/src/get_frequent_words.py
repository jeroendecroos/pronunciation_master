""" get_frequency_master gets the most frequent words for a language
"""
import StringIO
import requests

import resources
import language_codes
import commandline


def get_frequency_list(language, extended_return_value=False):
    """ returns a list of the most frequent words of a language
    the frequency lists are processede starting from the list hermitdave made
    see: https://github.com/hermitdave/FrequencyWords/
    or https://invokeit.wordpress.com/frequency-word-lists/

    Arguments:
        language=String     language for which to get the list
    Returns
        List        most frequent words in frequency-order
    """
    _language_code = FrequencySources.language_code(language)
    filestream = FrequencySources.frequency_filestream(_language_code)
    return _frequency_list_from_filestream(filestream, extended_return_value)


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


class FrequencySources(object):
    language_code = staticmethod(language_codes.HermitDave.map)
    frequency_filestream = staticmethod(_get_hermitdave_page)


def _frequency_list_from_filestream(filestream, extended_return_value=False):
    """Take a filestream and get the frequency list from it
    if extended_return -> list of (word, ranking, occurances)
    """
    freq_list = (line.strip().split() for line in filestream if line.strip())
    freq_list = [word if not extended_return_value else (word, i+1, int(freq))
                 for i, (word, freq) in enumerate(freq_list)]
    if not freq_list:
        raise RuntimeError("No entries found for creating a frequency list")
    return freq_list


if __name__ == '__main__':
    description = 'Get the word frequencies for a language'
    args = commandline.LanguageInput.parse_arguments(description)
    frequency_list = get_frequency_list(args.language)
    commandline.output_list(frequency_list[:5])
