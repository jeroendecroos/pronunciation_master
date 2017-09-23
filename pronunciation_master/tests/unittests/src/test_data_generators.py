from nose2.tools import params


from pronunciation_master.tests.testlib import testcase, project_vars
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
            {'a':1, 'b':2},
            )

    def test_args_and_kwargs(self):
        def func(a, b=2):
            pass
        self.assertEqual(
            data_generators.get_kwargs(func),
            {'b':2},
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

