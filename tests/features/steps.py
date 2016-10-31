from lettuce import *
import os

import testlib.project_vars
import testlib.testrun

@step('Given I have the language "(.*)"')
def i_have_the_language(step, language):
    world.language = language

@step
def ask_for_its_frequency_list(step):
    args = ['--language', world.language]
    path = os.path.join(testlib.project_vars.SRC_DIR, 'get_frequency_list.py')
    stdout, stderr, returncode = testlib.testrun.run_program(path, args)
    world.frequency_list = stdout.split('\n')[:-1]  ##remove last empty
    world.stderr = stderr

@step('I see the following at the top')
def check_list(step):
    to_check_list =step.multiline.split('\n')
    assert to_check_list == world.frequency_list

@step('Then I see the error message "(.*)"')
def check_error_message(step, error_message):
    assert error_message in world.stderr

