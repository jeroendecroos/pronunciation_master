""" library to interface the commandline for all scripts
"""
import os
import sys
import argparse
import logging

import resources

logging.basicConfig()


class ArgumentParser(argparse.ArgumentParser):
    """ interface to uniformize input arguments
    """
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def add_language(self, required=True):
        self.add_argument(
            '--language', dest='language', required=required,
            help='the language we want the data for')

    def add_word(self):
        self.add_argument(
            '--word', dest='word', required=True,
            help='the word we want the pdata for')

    def add_maximum_words_to_try(self):
        self.add_argument(
            '--maximum_words_to_try', dest='maximum_words_to_try',
            required=False, default=10, type=int,
            help='maximum number of words to test the pronunciation for')

    def add_minimum_examples(self):
        self.add_argument(
            '--minimum_examples', dest='minimum_examples',
            required=False, default=0, type=int,
            help='stop searching when minimum amount is reached')

    def add_maximum_examples(self):
        self.add_argument(
            '--maximum_examples', dest='maximum_examples',
            required=False, default=5, type=int,
            help='dont list more examples')

    def add_which_table(self):
        self.add_argument(
            '--which_table', dest='which_table',
            required=True, default='create_empty',
            choices=['pronunciations',
                     'phonemes',
                     'word_frequencies',
                     'create_empty'
                     ],
            help='which table to fill')

    def add_db_config(self):
        self.add_argument(
            '--db_config', dest='db_config',
            required=True, default=resources.db_config,
            help='configuration for database')

    def add_arguments_by_name(self, *args):
        for argument in args:
            method_name = 'add_'+argument
            method = getattr(self, method_name)
            method()


class CommonArguments(object):
    @classmethod
    def parse_arguments(cls, description, argv=None, extra_arguments=tuple()):
        argv = sys.argv[1:] if argv is None else argv
        parser = ArgumentParser(description=description)
        cls._add_arguments(parser)
        parser.add_arguments_by_name(*extra_arguments)
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


class LanguageDatabaseInput(CommonArguments):
    @staticmethod
    def _add_arguments(parser):
        parser.add_language(required=False)
        parser.add_which_table()
        parser.add_db_config()


def output_warnings(warnings, out=None):
    logger = logging.getLogger()
    if out:
        stream_handler = logging.StreamHandler(out)
        logger.addHandler(stream_handler)
    for warning in warnings:
        logger.warning(warning)


def output_list(iterable, out=sys.stdout):
    for item in iterable:
        out.write(item.encode('utf8') + os.linesep)


def output_dict(iterable, out=sys.stdout):
    for key, values in iterable.items():
        formatted_values = ', '.join(values).encode('utf8')
        formatted_key = key.encode('utf8')
        line = '{}: {}'.format(formatted_key, formatted_values)
        out.write(line + os.linesep)
