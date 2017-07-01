import abc
import iso639


def iso639_key(fun):
    """ wrapper to convert the input key to the appropriate format
    """
    def new_fun(self, key):
        correct_key = key.capitalize()
        value = fun(self, correct_key)
        return value
    return new_fun


class ISO639(object):
    """ ISO639 language code container
    """
    __metaclass__ = abc.ABCMeta

    @iso639_key
    def __getitem__(self, key):
        return self._get_entry(key)

    @iso639_key
    def __contains__(self, key):
        try:
            if self._get_entry(key):
                return True
            else:
                return False
        except KeyError:
            return False

    @abc.abstractmethod
    def _get_entry(self, key):
        ''' get a specific entry for a value key
        '''


class ISO639_2(ISO639):
    def _get_entry(self, key):
        return iso639.languages.get(name=key).part1


class ISO639_3(ISO639):
    def _get_entry(self, key):
        return iso639.languages.get(name=key).part3


class ISO639_Names(ISO639):
    def _get_entry(self, key):
        return iso639.languages.get(name=key).name


class LanguageCodes(object):
    """abstract class to map different language codes to each other
    sub classes need to implement the code-mapping
    """
    __metaclass__ = abc.ABCMeta
    codes = {}

    @classmethod
    def map(cls, language):
        language = language.lower()
        cls.check_valid_language(language)
        return cls.codes[language].lower()

    @classmethod
    def check_valid_language(cls, language):
        if language not in cls.codes:
            raise ValueError("Language '{}' is not known".format(language))


class HermitDave(LanguageCodes):
    """ mapping to serve HermitDave word frequency mapping
    """
    codes = ISO639_2()


class Phoibe(LanguageCodes):
    """ mapping to serve phoibe.com
    """
    codes = ISO639_3()


class Wiktionary(LanguageCodes):
    """ mapping to serve wiktionary
    """
    codes = ISO639_Names()
