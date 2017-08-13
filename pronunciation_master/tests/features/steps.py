import collections
import contextlib
import itertools
import json
import os
import re
import sqlalchemy
import sqlalchemy_utils

from lettuce import world, step

import testlib.project_vars
import testlib.testrun


DB_CONFIG_FILEPATH = os.path.join(testlib.project_vars.ASSETS_DIR, 'db_config.test.json')


@step('Given I have the language "(.*)"')
def i_have_the_language(_, language):
    world.language = language


@step('Given I have the word "(.*)"')
def i_have_the_word(_, word):
    world.word = word


@step(u'Given I want to try maximum "(.*)" words')
def given_i_want_to_try_maximum_N_words(_, maximum_words_to_try):
    world.maximum_words_to_try = maximum_words_to_try


@step("Given there is the database '(.*)'")
def given_there_is_the_database(_, database_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    if not sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.create_database(engine.url)
    world.database = database_name


@step("Given there is not the database '(.*)'")
def given_there_is_not_the_database(_, database_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    if sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.drop_database(engine.url)
    world.database = database_name


@step(u'I want to get minimum "(.*)" examples')
def given_i_want_to_get_minimum_X_examples(_, minimum_examples):
    world.minimum_examples = minimum_examples


@step(u'I want to get maximum "(.*)" examples')
def given_i_want_to_get_maximum_X_examples(_, maximum_examples):
    world.maximum_examples = maximum_examples


@step
def ask_for_its_frequency_list(_):
    _external_program_runner(
        'get_frequent_words.py',
        ['language'],
        _stdout_list_parser
        )


@step
def ask_for_its_phonemes(_):
    _external_program_runner(
        'get_phonemes.py',
        ['language'],
        _stdout_list_parser
        )


@step
def ask_for_pronunciation_examples(_):
    _external_program_runner(
        'get_pronunciation_examples.py',
        [
            'language',
            'maximum_words_to_try',
            'minimum_examples',
            'maximum_examples'],
        _stdout_dict_parser
        )


@step
def ask_for_its_pronunciations(_):
    _external_program_runner(
        'get_pronunciations.py',
        ['language', 'word'],
        )


@step('ask to create an empty database "(.*)"')
def ask_to_create_an_empty_database(_, database_name):
    world.db_config = DB_CONFIG_FILEPATH
    world.which_table = 'create_empty'
    _external_program_runner(
        'store_data.py',
        ['db_config', 'which_table'],
        )


@step(u'When I ask to store the "(.*)"')
def when_i_ask_to_store_its_data(_, which_table):
    world.db_config = DB_CONFIG_FILEPATH
    world.which_table = which_table
    _external_program_runner(
        'store_data.py',
        arguments = [
            'db_config',
            'which_table',
            'language',
            ],
        )


@step('I see the following at the top')
def check_list(step):
    to_check_list = step.multiline.split('\n')
    assert to_check_list == world.stdout


@step('I see the following tables in the database')
def check_tables_database(step):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)
    tables = [table.name for table in metadata.tables.values()]
    to_check_list = step.multiline.split('\n')
    for value in to_check_list:
        assert value in tables, (value, tables)


@step('I find the following in the table "(.*)"')
def in_the_table(step, table_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    columns = ', '.join("'{}'".format(x)
                        for x in step.hashes[0].keys())
    with engine.connect() as connection:
        statement = sqlalchemy.sql.text(
                " SELECT " + columns +
                " FROM " + table_name +
                " WHERE language='"+world.language+"';"
                )
        results = connection.execute(statement)
    assert results == step.hashes


@step('I see the following in the list')
def check_in_list(step):
    to_check_list = step.multiline.split('\n')
    for check_value in to_check_list:
        assert check_value.encode('utf8') in world.stdout


@step('I see the following in the dict-list')
def check_dict(step):
    tests = _transform_lettuce_hashes_into_dict(step.hashes)
    for test_key, test_values in tests.iteritems():
        for value in test_values:
            debug_text = (value, test_key, world.stdout[test_key])
            assert value in world.stdout[test_key], debug_text


@step('I don\'t see the following in the dict-list')
def check_negative_dict(step):
    tests = _transform_lettuce_hashes_into_dict(step.hashes)
    for test_key, test_values in tests.iteritems():
        for value in test_values:
            debug_text = (value, test_key, world.stdout[test_key])
            assert value not in world.stdout[test_key], debug_text


@step('Then I see the error message "(.*)"')
def check_error_message(_, error_message):
    assert error_message in world.stderr, world.stderr


@step('Then I "(.*)" see the warning message "(.*)"')
def check_warning_message(_, in_log, warning_message):
    warning_message = warning_message.encode('utf8')
    if in_log == "do":
        assert warning_message in world.stdout_warnings
    elif in_log == "don't":
        assert warning_message not in world.stdout_warnings
    else:
        raise Exception("in_log value is not valid for this lettuce step")


############################
#
#  UTILS
#
############################


def _external_program_runner(program, arguments=tuple(), parser=None):
    arguments = {'--{}'.format(a): getattr(world, a)
                 for a in arguments if hasattr(world, a)}
    arguments = list(itertools.chain.from_iterable(arguments.items()))
    path = os.path.join(testlib.project_vars.SRC_DIR, program)
    stdout, stderr, _ = testlib.testrun.run_program(path, arguments)
    world.stdout_warnings, world.stderr = _seperate_warning_lines(stderr)
    world.stdout = parser(stdout) if parser else stdout


def _transform_lettuce_hashes_into_dict(hashes):
    new_dict = collections.defaultdict(list)
    [new_dict[entry['key']].append(entry['value']) for entry in hashes]
    return new_dict


def _seperate_warning_lines(stderr):
    indicator = "WARNING"
    lines = stderr.split('\n')
    warnings = [l[len(indicator):] for l in lines if l.startswith(indicator)]
    stderr = [l for l in lines if not l.startswith(indicator)]
    return '\n'.join(warnings), '\n'.join(stderr)


def _stdout_list_parser(stdout):
    return stdout.split('\n')[:-1]  # remove last empty


def _stdout_dict_parser(stdout):
    new_dict = {}
    pattern = re.compile('^(.*): (.*)$')
    for line in _stdout_list_parser(stdout):
        m = re.search(pattern, line)
        phoneme = m.group(1)
        pronunciations = m.group(2).split(',')
        if phoneme in new_dict:
            error_template = "we have a double entry for '{}' in the output"
            raise Exception(error_template.format(phoneme))
        new_dict[phoneme] = [l.strip() for l in pronunciations]
    return new_dict


def _database_engine(db_config):
    '''Returns a connection and a metadata object'''
    with open(db_config) as json_data_file:
        DB_CONFIG_DICT = json.load(json_data_file)
    DB_CONN_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{database}"
    DB_CONN_URI_DEFAULT = (DB_CONN_FORMAT.format(
         **DB_CONFIG_DICT
    ))
    return sqlalchemy.create_engine(DB_CONN_URI_DEFAULT, client_encoding='utf8')
