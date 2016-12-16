import tests.testlib.testcase as testcase
import pronunciation_master.commandline as commandline


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

    def test_wrong_argument(self):
        parser = commandline.ArgumentParser()
        with self.assertRaises(SystemExit):
            parser.parse_args(['--something', 'd'])
