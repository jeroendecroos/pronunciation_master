import abc

class LanguageCodes(object):
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
    codes = {'dutch': 'nl'}

class Phoibe(LanguageCodes):
    codes = {'dutch': 'nld'}

class Wiktionary(LanguageCodes):
    codes = {'dutch': 'dutch'}
