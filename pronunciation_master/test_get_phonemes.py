import os
import unittest
import tempfile

import tests.testlib.testcase as testcase
import get_phonemes

def create_phoneme_data_source_phiobe(filepath, language, phonemes):
    with open(filepath, 'wb') as filestream:
        filestream.write('LanguageCode\tPhoneme\n')
        for phoneme in phonemes:
            filestream.write('{}\t{}\n'.format(language, phoneme))


class PhonemesTest(testcase.BaseTestCase):
    def setUp(self):
        _, self.temporary_source = tempfile.mkstemp()

    def tearDown(self):
        os.remove(self.temporary_source)

    def test_get_all_phonemes(self):
        phonemes = get_phonemes.PhonemesCollector('dutch')
        phoneme_list = ['p1', 'p2']
        create_phoneme_data_source_phiobe(self.temporary_source, 'nld', phoneme_list)
        phonemes.parse_source(self.temporary_source)
        ret = phonemes.get_all_phonemes()
        self.assertItemsEqual(ret, phoneme_list)


if __name__ == '__main__':
    unittest.main()
