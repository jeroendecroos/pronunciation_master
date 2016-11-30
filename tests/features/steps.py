from lettuce import *
import os

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

def ask_for_list_for_language(program):
    args = ['--language', world.language]
    path = os.path.join(testlib.project_vars.SRC_DIR, program)
    stdout, stderr, returncode = testlib.testrun.run_program(path, args)
    world.stdout = stdout.split('\n')[:-1]  ##remove last empty
    world.stderr = stderr

@step('I see the following at the top')
def check_list(step):
    to_check_list =step.multiline.split('\n')
    assert to_check_list == world.stdout

@step('I see the following in the list')
def check_list(step):
    to_check_list =step.multiline.split('\n')
    for check_value in to_check_list:
        assert check_value in world.stdout

@step('Then I see the error message "(.*)"')
def check_error_message(step, error_message):
    assert error_message in world.stderr

