""" library to interface the commandline for all scripts
"""
import os
import sys
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


class CommonArguments(object):

    @classmethod
    def parse_arguments(cls, description, argv=None):
        argv = sys.argv[1:] if argv is None else argv
        parser = ArgumentParser(description=description)
        cls._add_arguments(parser)
        return parser.parse_args(argv)

    @staticmethod
    def _add_arguments(parser):
        pass


class LanguageInput(CommonArguments):
    @staticmethod
    def _add_arguments(parser):
        parser.add_language()


class LanguageAndWordInput(CommonArguments):
    @staticmethod
    def _add_arguments(parser):
        parser.add_language()
        parser.add_word()


def output_list(iterable, out=sys.stdout):
    for item in iterable:
        out.write(item.encode('utf8') + os.linesep)


def output_dict(iterable, out=sys.stdout):
    for key, values in iterable.items():
        formatted_values = ', '.join(values).encode('utf8')
        formatted_key = key.encode('utf8')
        line = '{}: {}'.format(formatted_key, formatted_values)
        out.write(line + os.linesep)
