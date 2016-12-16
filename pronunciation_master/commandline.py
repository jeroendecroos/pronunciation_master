""" library to interface the commandline for all scripts
"""
import argparse


class ArgumentParser(argparse.ArgumentParser):
    """ interface to uniformize input arguments
    """
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def add_language(self):
        self.add_argument(
            '--language', dest='language', required=True,
            help='the language we want the pronuncations for')

    def add_word(self):
        self.add_argument(
            '--word', dest='word', required=True,
            help='the word we want the pronunciations for')


class CommonArgumentParser(object):

    @classmethod
    def get_arguments(cls, description):
        parser = ArgumentParser(description=description)
        cls._add_arguments(parser)
        return parser.parse_args()

    @staticmethod
    def _add_arguments(parser):
        pass


class LanguageInput(CommonArgumentParser):
    @staticmethod
    def _add_arguments(parser):
        parser.add_language()


class LanguageAndWordInput(CommonArgumentParser):
    @staticmethod
    def _add_arguments(parser):
        parser.add_language()
        parser.add_word()


def output_list(iterable):
    for item in iterable:
        print(item.encode('utf8'))


def output_dict(iterable):
    for key, values in iterable.items():
        formatted_values = ', '.join(values).encode('utf8')
        formatted_key = key.encode('utf8')
        print('{}: {}'.format(formatted_key, formatted_values))
