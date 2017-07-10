import os
import itertools
import collections
import re

from lettuce import world, step

import testlib.project_vars
import testlib.testrun


@step('Given I have the language "(.*)"')
def i_have_the_language(_, language):
    world.language = language


@step('Given I have the word "(.*)"')
def i_have_the_word(_, word):
    world.word = word


@step(u'Given I want to try maximum "(.*)" words')
def given_i_want_to_try_maximum_N_words(_, maximum_words_to_try):
    world.maximum_words_to_try = maximum_words_to_try


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
        _stdout_list_parser
        )


@step('I see the following at the top')
def check_list(step):
    to_check_list = step.multiline.split('\n')
    assert to_check_list == world.stdout


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
            assert value in world.stdout[test_key], (value, test_key, world.stdout[test_key])


@step('I don\'t see the following in the dict-list')
def check_negative_dict(step):
    tests = _transform_lettuce_hashes_into_dict(step.hashes)
    for test_key, test_values in tests.iteritems():
        for value in test_values:
            assert value not in world.stdout[test_key]


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


def _external_program_runner(program, arguments, parser):
    arguments = {'--{}'.format(a): getattr(world, a)
                 for a in arguments if hasattr(world, a)}
    arguments = list(itertools.chain.from_iterable(arguments.items()))
    path = os.path.join(testlib.project_vars.SRC_DIR, program)
    stdout, stderr, _ = testlib.testrun.run_program(path, arguments)
    world.stdout_warnings, world.stderr = _seperate_warning_lines(stderr)
    world.stdout = parser(stdout)


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
