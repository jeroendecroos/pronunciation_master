""" get_frequency_master gets the most frequent words for a language
"""
import argparse
import csv

import language_codes
import resources

class PhonemesCollector(object):
    def __init__(self, language):
        self.language = language
        self.language_code = self._get_language_code()
        self.all_data = []

    def parse_source(self, filepath):
        """ Use a source to populate the Phonemes object with data
        currently parsed from a fixed file, could benefit from an SQL like database"""
        with open(filepath, 'rb') as tsv_file:
            tsv_reader = csv.DictReader(tsv_file, delimiter='\t')
            for row in tsv_reader:
                if row['LanguageCode'] == self.language_code:
                    self._add_datarow(row)

    def _add_datarow(self, row):
        self.all_data.append(row)

    def _get_language_code(self):
        return language_codes.Phoibe.map(self.language)

    def get_all_phonemes(self):
        return set(row['Phoneme'] for row in self.all_data)

def get_phonemes(language):
    phoibe_data = resources.phoible_database
    phonemes_collector = PhonemesCollector(language)
    phonemes_collector.parse_source(phoibe_data)
    return phonemes_collector.get_all_phonemes()

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
    for phoneme in phonemes:
        print(phoneme)
