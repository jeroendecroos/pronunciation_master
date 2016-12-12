""" get_frequency_master gets the most frequent words for a language
"""
import csv
import codecs

import language_codes
import resources
import commandline

class PhonemesCollector(object):
    """ Hold information about all the phonemes in a language
        it is populated by calling the parse_source
    """
    def __init__(self, language):
        self.language = language
        self.language_code = self._get_language_code()
        self.all_data = []

    def parse_source(self, filepath):
        """ Use a source to populate the Phonemes object with data
        currently parsed from a fixed file, could benefit from an SQL like database"""
        with codecs.open(filepath, 'r') as tsv_file:
            tsv_reader = csv.DictReader(tsv_file, delimiter='\t')
            for row in tsv_reader:
                if row['LanguageCode'] == self.language_code:
                    self._add_datarow(row)

    def _add_datarow(self, row):
        self.all_data.append(row)

    def _get_language_code(self):
        return language_codes.Phoibe.map(self.language)

    def get_all_phonemes(self):
        """ get a set of all the phonemes for the language of the phonemeCollector
        """
        return set(row['Phoneme'].decode('utf8') for row in self.all_data)

def get_phonemes(language):
    """Main entry point for the module
    will return a set of phonemes for the given language
    Arguments:
        language=language for which to get the phonemes
    Returns:
        set of phonemes
    """
    phoibe_data = resources.phoible_database
    phonemes_collector = PhonemesCollector(language)
    phonemes_collector.parse_source(phoibe_data)
    return phonemes_collector.get_all_phonemes()


if __name__ == '__main__':
    args = commandline.LanguageInput.get_arguments('Get the phonemes from a language')
    phonemes = get_phonemes(args.language)
    commandline.output_list(phonemes)
