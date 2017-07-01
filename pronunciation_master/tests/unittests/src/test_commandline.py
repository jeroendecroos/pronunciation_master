import os
from StringIO import StringIO
from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import commandline


class ArgumentParserTest(testcase.BaseTestCase):

    def test_init(self):
        commandline.ArgumentParser('description')

    def test_add_language(self):
        parser = commandline.ArgumentParser()
        parser.add_language()
        args = parser.parse_args(['--language', 'd'])
        self.assertEqual(args.language, 'd')

    def test_add_word(self):
        parser = commandline.ArgumentParser()
        parser.add_word()
        args = parser.parse_args(['--word', 'd'])
        self.assertEqual(args.word, 'd')

    def test_add_maximum_words_to_try(self):
        parser = commandline.ArgumentParser()
        parser.add_maximum_words_to_try()
        args = parser.parse_args(['--maximum_words_to_try', '1'])
        self.assertEqual(args.maximum_words_to_try, 1)

    def test_add_minimum_examples(self):
        parser = commandline.ArgumentParser()
        parser.add_minimum_examples()
        args = parser.parse_args(['--minimum_examples', '1'])
        self.assertEqual(args.minimum_examples, 1)

    def test_add_arguments_by_name(self):
        parser = commandline.ArgumentParser()
        parser.add_arguments_by_name("word")
        args = parser.parse_args(['--word', 'd'])
        self.assertEqual(args.word, 'd')

    def test_wrong_argument(self):
        parser = commandline.ArgumentParser()
        with self.assertRaises(SystemExit):
            parser.parse_args(['--nogoodargument', 'unittest'])


class CommonArgumentParserTest(testcase.BaseTestCase):
    def test_getting_through(self):
        parser = commandline.CommonArguments
        parser.parse_arguments('h', [])


class LanguageInputTest(testcase.BaseTestCase):
    def test_arguments(self):
        parser = commandline.LanguageInput
        test_arguments = ['--language', 'test']
        args = parser.parse_arguments('h', test_arguments)
        self.assertEqual(args.language, 'test')


class LanguageAndWordInputTest(testcase.BaseTestCase):
    def test_arguments(self):
        parser = commandline.LanguageAndWordInput
        test_arguments = ['--language', 'test',
                          '--word', 'wtest']
        args = parser.parse_arguments('h', test_arguments)
        self.assertEqual(args.language, 'test')
        self.assertEqual(args.word, 'wtest')


def run_output_command(fun, items):
    out = StringIO()
    fun(items, out=out)
    return out.getvalue()


class OutputListTest(testcase.BaseTestCase):
    @params(
             ('no line',
              [],
              ''
              ),
             ('one line',
              ['1'],
              '1' + os.linesep
              ),
             ('two lines',
              ['1', '2'],
              '1' + os.linesep + '2' + os.linesep
              ),)
    def test_one_line(self, _, items, expected):
        fun = commandline.output_list
        output = run_output_command(fun, items)
        self.assertEqual(output, expected)


class OutputWarningTest(testcase.BaseTestCase):
    @params(
             ('no line',
              [],
              ''
              ),
             ('one line',
              ['1'],
              '1' + os.linesep
              ),
             ('two lines',
              ['1', '2'],
              '1' + os.linesep + '2' + os.linesep
              ),)
    def test_one_line(self, _, items, expected):
        fun = commandline.output_warnings
        output = run_output_command(fun, items)
        self.assertEqual(output, expected)


class OutputDictTest(testcase.BaseTestCase):
    @params(
             ('empty',
              {},
              ''
              ),
             ('one key',
              {'1': ''},
              '1: '+os.linesep
              ),
             ('one key, one value',
              {'1': ['v']},
              '1: v'+os.linesep
              ),
             ('one key, two values',
              {'1': ['v', 'w']},
              '1: v, w'+os.linesep
              ),
             ('two keys',
              {'1': [], '2': []},
              '1: ' + os.linesep + '2: ' + os.linesep
              ),)
    def test_one_line(self, _, items, expected):
        fun = commandline.output_dict
        output = run_output_command(fun, items)
        self.assertEqual(output, expected)
