from nose2.tools import params

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import data_generators


class GetKwargsTest(testcase.BaseTestCase):
    def test_no_args(self):
        def func():
            pass
        self.assertEqual(
            data_generators.get_kwargs(func),
            {},
            )

    def test_no_kwargs(self):
        def func(e):
            pass
        self.assertEqual(
            data_generators.get_kwargs(func),
            {},
            )

    def test_one_kwargs(self):
        def func(a=1):
            pass
        self.assertEqual(
            data_generators.get_kwargs(func),
            {'a': 1},
            )

    def test_two_kwargs(self):
        def func(a=1, b=2):
            pass
        self.assertEqual(
            data_generators.get_kwargs(func),
            {'a': 1, 'b': 2},
            )

    def test_args_and_kwargs(self):
        def func(a, b=2):
            pass
        self.assertEqual(
            data_generators.get_kwargs(func),
            {'b': 2},
            )


class RowGeneratorTest(testcase.BaseTestCase):
    @params(('one value',
             (lambda x: x),
             ['col1'],
             [{'language': 'bla', 'col1': x} for x in range(10)]
             ),
            ('tuple',
             (lambda x: (x, x**2)),
             ['col1', 'col2'],
             [{'language': 'bla', 'col1': x, 'col2': x**2} for x in range(10)]
             ),
            ('dict',
             (lambda x: {'col1': x, 'col2': x**2}),
             ['col1', 'col2'],
             [{'language': 'bla', 'col1': x, 'col2': x**2} for x in range(10)]
             ),
            ('namespace',
             (lambda x: type('waw', (), {'col1': x, 'col2': x**2})),
             ['col1', 'col2'],
             [{'language': 'bla', 'col1': x, 'col2': x**2} for x in range(10)]
             ),
            ('dict_reductor',
             (lambda x: {'col1': x, 'col2': x**2}),
             ['col1'],
             [{'language': 'bla', 'col1': x} for x in range(10)]
             ),
            )
    def test_one_value(self, _, value_creator, column_names, expected_values):
        class Module:  # we mock directly with a class iso module mock
            @staticmethod
            def function(_):
                for i in range(10):
                    yield value_creator(i)
        gen = data_generators.RowGenerator(Module, "function", column_names)
        self.assertEqual(
            [x for x in gen.get()('bla')],
            expected_values
            )

    @params(('add',
             (lambda x: {'col1': [str(x), str(x**2)]}),
             ['col1'],
             [{'language': 'bla', 'col1': str(x)+str(x**2)} for x in range(10)]
             ),
            )
    def test_list_value(self, _, value_creator, column_names, expected_values):
        class Module:  # we mock directly with a class iso module mock
            @staticmethod
            def function(_):
                for i in range(10):
                    yield value_creator(i)
        gen = data_generators.RowGenerator(
            Module, "function",
            column_names,
            list_modifier=lambda x: ''.join(x))
        self.assertEqual(
            [x for x in gen.get()('bla')],
            expected_values
            )

    def test_args_and_kwargs(self):
        class Module:  # we mock directly with a class iso module mock
            @staticmethod
            def function(language='', y=4):
                pass
        gen = data_generators.RowGenerator(Module, "function", "")
        self.assertEqual(
            gen.get_possible_options(),
            {'y': 4},
            )

    def test_add_options(self):
        class Module:  # we mock directly with a class iso module mock
            @staticmethod
            def function(language='', y=4):
                pass
        gen = data_generators.RowGenerator(Module, "function", "")
        gen.add_options(type('n', (), {'y': 4}))
        self.assertEqual(
            gen.kwargs,
            {'y': 4},
            )


class RowGeneratorsTest(testcase.BaseTestCase):
    def test_args_and_kwargs(self):
        class Module:  # we mock directly with a class iso module mock
            @staticmethod
            def function(language='', y=4):
                pass
        gen = data_generators.RowGenerator(Module, "function", "")

        class RowGenerators(data_generators.RowGenerators):
            row_generators = {"us": gen}
        self.assertEqual(
            RowGenerators.get_all_options(),
            {'us': {'y': 4}},
            )
