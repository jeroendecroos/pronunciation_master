from lettuce import *
import os
import itertools
import collections
import re

import testlib.project_vars
import testlib.testrun

@step('Given I have the language "(.*)"')
def i_have_the_language(step, language):
    world.language = language

@step('Given I have the word "(.*)"')
def i_have_the_word(step, word):
    world.word = word


@step
def ask_for_its_frequency_list(step):
    ask_for_list_for_language('get_frequent_words.py')

@step
def ask_for_its_phonemes(step):
    ask_for_list_for_language('get_phonemes.py')

@step
def ask_for_its_pronunciation_examples(step):
    ask_for_dict_for_language('get_pronunciation_examples.py')

@step
def ask_for_its_pronunciations(step):
    command_line_arguments = {
        '--language': world.language,
        '--word': world.word}
    ask_for_list('get_pronunciations.py', command_line_arguments)

def ask_for_list_for_language(program):
    command_line_arguments = {'--language': world.language}
    ask_for_list(program, command_line_arguments)

def ask_for_dict_for_language(program):
    command_line_arguments = {'--language': world.language}
    ask_for_dict(program, command_line_arguments)

def ask_for_list(program, command_line_arguments):
    ask_for_something_to_parse(program, command_line_arguments, _stdout_list_parser)

def ask_for_dict(program, command_line_arguments):
    ask_for_something_to_parse(program, command_line_arguments, _stdout_dict_parser)

def ask_for_something_to_parse(program, command_line_arguments, parser):
    arguments = list(itertools.chain.from_iterable(command_line_arguments.items()))
    path = os.path.join(testlib.project_vars.SRC_DIR, program)
    stdout, stderr, returncode = testlib.testrun.run_program(path, arguments)
    world.stdout = parser(stdout)  ##remove last empty
    world.stderr = stderr

@step('I see the following at the top')
def check_list(step):
    to_check_list =step.multiline.split('\n')
    assert to_check_list == world.stdout

@step('I see the following in the list')
def check_list(step):
    to_check_list =step.multiline.split('\n')
    for check_value in to_check_list:
        assert check_value.encode('utf8') in world.stdout

@step('I see the following in the dict-list')
def check_dict(step):
    tests = _transform_lettuce_hashes_into_dict(step.hashes)
    for test_key, test_values in tests.iteritems():
        for value in test_values:
            assert value in world.stdout[test_key]

def _transform_lettuce_hashes_into_dict(hashes):
    new_dict = collections.defaultdict(list)
    [new_dict[entry['key']].append(entry['value']) for entry in hashes]
    return new_dict

def _stdout_list_parser(stdout):
    return stdout.split('\n')[:-1]  ##remove last empty

def _stdout_dict_parser(stdout):
    new_dict = {}
    pattern = re.compile('^(.*): (.*)$')
    for line in _stdout_list_parser(stdout):
        m = re.search(pattern, line)
        phoneme = m.group(1)
        pronunciations = m.group(2).split(',')
        if phoneme in new_dict:
            raise Exception("we have a double entry for '{}' in the output".format(phoneme))
        new_dict[phoneme] = pronunciations
    return new_dict

@step('Then I see the error message "(.*)"')
def check_error_message(step, error_message):
    assert error_message in world.stderr

