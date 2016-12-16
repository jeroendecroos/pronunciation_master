import abc


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
    codes = {'dutch': 'nl'}


class Phoibe(LanguageCodes):
    """ mapping to serve phoibe.com
    """
    codes = {'dutch': 'nld'}


class Wiktionary(LanguageCodes):
    """ mapping to serve wiktionary
    """
    codes = {'dutch': 'dutch'}
