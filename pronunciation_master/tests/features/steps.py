import collections
import itertools
import json
import os
from pymongo import MongoClient
import re
import sqlalchemy
import sqlalchemy_utils
import tempfile

from lettuce import before, after, step

import testlib.project_vars
import testlib.testrun


DB_CONFIG_FILEPATH = os.path.join(
    testlib.project_vars.ASSETS_DIR,
    'db_config.test.json')


@before.each_scenario
def add_context_to_scenario(scenario):
    scenario.context = {}


@after.each_scenario
def clear_context(scenario):
    scenario.context.clear()


@step('Given I have the language "(.*)"')
def i_have_the_language(step, language):
    step.scenario.context['language'] = language


@step('Given I have the word "(.*)"')
def i_have_the_word(step, word):
    step.scenario.context['word'] = word


@step(u'Given I want to try maximum "(.*)" words')
def given_i_want_to_try_maximum_N_words(step, maximum_words_to_try):
    step.scenario.context['maximum_words_to_try'] = maximum_words_to_try


@step("Given there is the database '(.*)'")
def given_there_is_the_database(step, database_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    if not sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.create_database(engine.url)
    step.scenario.context['database'] = database_name


@step("Given there is not the database '(.*)'")
def given_there_is_not_the_database(step, database_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    if sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.drop_database(engine.url)
    step.scenario.context['database'] = database_name


@step(u'I want to get minimum "(.*)" examples')
def given_i_want_to_get_minimum_X_examples(step, minimum_examples):
    step.scenario.context['minimum_examples'] = minimum_examples


@step(u'I want to get maximum "(.*)" examples')
def given_i_want_to_get_maximum_X_examples(step, maximum_examples):
    step.scenario.context['maximum_examples'] = maximum_examples


@step(u'Given there is the following in the table "([^"]*)":')
def given_there_is_the_following_in_the_table_group1(step, table_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    hashes = _normalize_hashes(step.hashes)
    with engine.connect() as connection:
        for row in hashes:
            row['language'] = step.scenario.context['language']
            columns = ", ".join(row.keys())
            values = ", ".join("'{}'".format(x) for x in row.values())
            statement = sqlalchemy.sql.text(
                    " INSERT INTO " + table_name +
                    " (" + columns + ")"
                    " VALUES ("+values+");"
                    )
            connection.execute(statement)


@step(u'Given I have a mongodb with raw input')
def given_i_have_a_mongodb_with_raw_input(step):
    client = MongoClient()
    db = client.pronunciation_master_test
    collection = db.wiktionary_raw
    document = {row['key']: row['value'] for row in step.hashes}
    collection.insert_one(document)


@step(u'Given I have a mongodb with raw input per language')
def given_i_have_a_mongodb_with_raw_input_per_language(step):
    client = MongoClient()
    db = client.pronunciation_master_test
    collection = db.wiktionary_raw_subdivided
    document = {row['key']: row['value'] for row in step.hashes}
    collection.insert_one(document)


@step(u'Given I have a mongodb with per language and per word')
def given_i_have_a_mongodb_with_per_language_and_per_word(step):
    client = MongoClient()
    db = client.pronunciation_master_test
    collection = db.wiktionary_ipa
    step.scenario.context['local'] = 'pronunciation_master_test'
    for row in step.hashes:
        document = {
            'language': step.scenario.context['language'].capitalize(),
            'word': row['key'],
            'IPA': row['value'].split(',')
            }
        collection.insert_one(document)


@step(u'When I ask to process into language and category')
def when_i_ask_to_process_into_language_and_category(step):
    step.scenario.context['database'] = 'pronunciation_master_test'
    step.scenario.context['mongodb_table'] = "wiktionary_raw_subdivided"
    _external_program_runner(
        step,
        'process_mongodb.py',
        ['database'],
        )


@step(u'When I ask to process into pronunciation per language')
def when_i_ask_to_process_into_pronunciation_per_language(step):
    step.scenario.context['database'] = 'pronunciation_master_test'
    step.scenario.context['mongodb_table'] = "wiktionary_ipa"
    _external_program_runner(
        step,
        'process_mongodb_ipa.py',
        ['database'],
        )


@step(u'See the following in the mongodb json')
def i_see_the_following_in_the_mongodb_json(step):
    for row in step.hashes:
        if '[' in row['value']:
            row['value'] = eval(row['value'])
        mongodb_find = step.scenario.context['mongodb_find']
        assert mongodb_find[row['key']] == row['value']


@step(u'Given I want to get the data from the database "(.*)"')
def given_i_want_to_get_the_data_from_the_database(step, mode):
    step.scenario.context['db_config'] = DB_CONFIG_FILEPATH
    step.scenario.context['use_database'] = mode
    if hasattr(step.scenario.context, 'minimum_examples'):
        del step.scenario.context['minimum_examples']


@step(u'Given I have the wiktionary with entry:')
def given_i_have_the_wiktionary_with_entry(step):
    _, step.scenario.context['wiktionary'] = tempfile.mkstemp()
    with open(step.scenario.context['wiktionary'], 'wb') as outstream:
        outstream.write('<document>\n')
        outstream.write(step.multiline)
        outstream.write('<\document>\n')


@step(u'When I ask for to process into mongodb')
def when_i_ask_for_to_process_into_mongodb(step):
    step.scenario.context['database'] = 'pronunciation_master_test'
    step.scenario.context['mongodb_table'] = "wiktionary_raw"
    _external_program_runner(
        step,
        'wiktionary_to_db.py',
        ['wiktionary',
         'database'],
        )


@step('I have an empty mongodb')
def i_have_an_empty_mongodb(step):
    client = MongoClient()
    db = client.pronunciation_master_test
    db.wiktionary_raw.drop()
    db.wiktionary_raw_subdivided.drop()
    db.wiktionary_ipa.drop()
    client.drop_database('pronunciation_master_test')


@step(u'When I ask to find in the mongodb')
def when_i_ask_to_find_in_the_mongodb_one(step):
    client = MongoClient()
    db = client.pronunciation_master_test
    collection = getattr(db, step.scenario.context['mongodb_table'])
    document = {row['key']: row['value'] for row in step.hashes}
    step.scenario.context['mongodb_find'] = collection.find_one(document)
    if not step.scenario.context['mongodb_find']:
        raise Exception('dont find anzthing for {}'.format(document))


@step(u'Then I see the following in the mongodb')
def i_see_the_following_in_the_mongodb(step):
    for row in step.hashes:
        mongodb_value = step.scenario.context['mongodb_find'][row['key']]
        assert mongodb_value.strip() == row['value']


@step
def ask_for_its_frequency_list(step):
    _external_program_runner(
        step,
        'get_frequent_words.py',
        ['language'],
        _stdout_list_parser
        )


@step
def ask_for_its_phonemes(step):
    _external_program_runner(
        step,
        'get_phonemes.py',
        ['language'],
        _stdout_list_parser
        )


@step
def ask_for_pronunciation_examples(step):
    _external_program_runner(
        step,
        'get_pronunciation_examples.py',
        [
            'language',
            'maximum_words_to_try',
            'minimum_examples',
            'maximum_examples',
            'use_database',
            'db_config',
        ],
        _stdout_dict_parser
        )


@step
def ask_for_its_pronunciations(step):
    _external_program_runner(
        step,
        'get_pronunciations.py',
        ['language', 'word', 'local'],
        )


@step('ask to create an empty database "(.*)"')
def ask_to_create_an_empty_database(step, database_name):
    step.scenario.context['db_config'] = DB_CONFIG_FILEPATH
    step.scenario.context['which_table'] = 'create_empty'
    _external_program_runner(
        step,
        'store_data.py',
        ['db_config'],
        positional_arguments=[
            'which_table',
            ],
        )


@step(u'When I ask to store the "(.*)"')
def when_i_ask_to_store_its_data(step, which_table):
    step.scenario.context['db_config'] = DB_CONFIG_FILEPATH
    step.scenario.context['which_table'] = which_table
    _external_program_runner(
        step,
        'store_data.py',
        arguments=[
            'db_config',
            'language',
            ],
        positional_arguments=[
            'which_table',
            ],
        sub_arguments=['local'],
        )


@step(u'When I ask to store the "(.*)" with "(.*)"')
def i_ask_to_store_its_data_with_parameters(step, which_table, parameters):
    step.scenario.context['db_config'] = DB_CONFIG_FILEPATH
    step.scenario.context['which_table'] = which_table
    sub_arguments = dict(x.split("=") for x in parameters.split(','))
    for key, value in sub_arguments.iteritems():
        step.scenario.context[key] = value
    _external_program_runner(
        step,
        'store_data.py',
        arguments=[
            'db_config',
            'language',
            ],
        positional_arguments=[
            'which_table',
            ],
        sub_arguments=['local']+sub_arguments.keys(),
        )


@step('I see the following at the top')
def check_list(step):
    to_check_list = step.multiline.split('\n')
    assert to_check_list == step.scenario.context['stdout']


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
    maybe_in_the_table(step, False, table_name)


@step('I "(do not|do)" find the following in the table "(.*)"')
def maybe_in_the_table(step, dont_find, table_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    hashes = _normalize_hashes(step.hashes)
    columns = ', '.join(hashes[0].keys())
    with engine.connect() as connection:
        statement = sqlalchemy.sql.text(
                " SELECT " + columns +
                " FROM " + table_name +
                " WHERE language='"+step.scenario.context['language']+"';"
                )
        results = [dict(x) for x in connection.execute(statement)]
    for row in hashes:
        for key, values in row.iteritems():
            if isinstance(values, basestring) and '[' in values:
                row[key] = eval(values)
        if dont_find:
            assert row not in results, (results[:10], row)
        else:
            assert row in results, (results[:10], row)


@step('I find no duplicates in the table "(.*)" for the following columns')
def only_once_in_the_table(step, table_name):
    engine = _database_engine(DB_CONFIG_FILEPATH)
    columns = ', '.join(step.multiline.split('\n'))
    with engine.connect() as connection:
        statement = sqlalchemy.sql.text(
                " SELECT " + columns +
                " FROM " + table_name +
                " WHERE language='"+step.scenario.context['language']+"';"
                )
        results = [tuple(x) for x in connection.execute(statement)]
        assert len(set(results)) == len(results)


def _normalize_hashes(hashes):
    def _normalize_dict(d):
        new_d = {}
        for key, value in d.iteritems():
            if key.startswith('int:'):
                key = key[len('int:'):]
                value = int(value)
            new_d[key] = value
        return new_d
    return [_normalize_dict(row) for row in hashes]


@step('I see the following in the list')
def check_in_list(step):
    to_check_list = step.multiline.split('\n')
    for check_value in to_check_list:
        assert check_value.encode('utf8') in step.scenario.context['stdout']


@step('I see the following in the dict-list')
def check_dict(step):
    tests = _transform_lettuce_hashes_into_dict(step.hashes)
    for test_key, test_values in tests.iteritems():
        for value in test_values:
            stdout = step.scenario.context['stdout']
            debug_text = (
                value,
                test_key,
                stdout.get(test_key), stdout,
                )
            assert test_key in stdout, debug_text
            assert value in stdout[test_key], debug_text


@step('I don\'t see the following in the dict-list')
def check_negative_dict(step):
    tests = _transform_lettuce_hashes_into_dict(step.hashes)
    for test_key, test_values in tests.iteritems():
        for value in test_values:
            stdout = step.scenario.context['stdout']
            debug_text = (value, test_key, stdout[test_key])
            assert value not in stdout[test_key], debug_text


@step('Then I see the error message "(.*)"')
def check_error_message(step, error_message):
    stderr = step.scenario.context['stderr']
    assert error_message in stderr, stderr


@step('Then I see the approximate error message "(.*)"')
def check_approximate_error_message(step, error_message):
    stderr = step.scenario.context['stderr']
    assert re.search(error_message, stderr), stderr


@step('Then I "(.*)" see the warning message "(.*)"')
def check_warning_message(step, in_log, warning_message):
    warning_message = warning_message.encode('utf8')
    if in_log == "do":
        assert warning_message in step.scenario.context['stdout_warnings']
    elif in_log == "don't":
        assert warning_message not in step.scenario.context['stdout_warnings']
    else:
        raise Exception("in_log value is not valid for this lettuce step")

############################
#
#  UTILS
#
############################


def _external_program_runner(
        step,
        program,
        arguments=tuple(),
        parser=None,
        positional_arguments=tuple(),
        sub_arguments=tuple(),
        ):
    arguments = {'--{}'.format(a): step.scenario.context[a]
                 for a in arguments if a in step.scenario.context}
    arguments = list(itertools.chain.from_iterable(arguments.items()))
    arguments += [step.scenario.context[a] for a in positional_arguments]
    sub_arguments = {'--{}'.format(a): step.scenario.context[a]
                     for a in sub_arguments if a in step.scenario.context}
    arguments += list(itertools.chain.from_iterable(sub_arguments.items()))
    path = os.path.join(testlib.project_vars.SRC_DIR, program)
    command = [path] + arguments
    step.scenario.context.setdefault('commands', []).append(command)
    stdout, stderr, _ = testlib.testrun.run_program(path, arguments)
    context = step.scenario.context
    context['stdout_warnings'], context['stderr'] = _filter_stderr(stderr)
    context['stdout'] = parser(stdout) if parser else stdout


def _transform_lettuce_hashes_into_dict(hashes):
    new_dict = collections.defaultdict(list)
    [new_dict[entry['key']].append(entry['value']) for entry in hashes]
    return new_dict


def _filter_stderr(stderr):
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
    engine = sqlalchemy.create_engine(
        DB_CONN_URI_DEFAULT,
        client_encoding='utf8')
    return engine
