import abc


class ISO639(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __getitem__(self, key):
        """ This method should return a isoX value for the language key
        """

    @abc.abstractmethod
    def __contains__(self, key):
        """ This method should check if it has an ISOX entry language key
        """


class ISO639_2(ISO639):
    codes = {'dutch': 'nl'}

    def __getitem__(self, key):
        return self.codes[key]

    def __contains__(self, key):
        return key in self.codes


class ISO639_3(ISO639):
    codes = {'dutch': 'nld'}

    def __getitem__(self, key):
        return self.codes[key]

    def __contains__(self, key):
        return key in self.codes


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
        return cls.codes[language]

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
    codes = {'dutch': 'dutch'}
