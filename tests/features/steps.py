from lettuce import *
import os

import testlib.project_vars
import testlib.testrun

@step('Given I have the language "(.*)"')
def i_have_the_language(step, language):
    world.language = language

@step
def ask_for_its_frequency_list(step):
    args = ['--language', 'dutch']
    path = os.path.join(testlib.project_vars.SRC_DIR, 'get_frequency_list')
    stdout, stderr, returncode = testlib.testrun.run_program(path, args)
    world.frequency_list = stderr.split('\n')

@step('I see the following at the top')
def check_list(step):
    assert step.multiline == world.frequency_list[:5]

