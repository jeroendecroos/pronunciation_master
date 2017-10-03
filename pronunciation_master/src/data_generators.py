import itertools

import get_frequent_words
import get_phonemes
import get_pronunciations
import get_pronunciation_examples


class RowGenerator(object):
    def __init__(self, module, function, column_names, list_modifier=None, buffer_size=None, **kwargs):
        self.data_provider = getattr(module, function)
        self.column_names=column_names
        self.list_modifier = list_modifier
        self.kwargs = kwargs
        self.buffer_size=buffer_size

    def add_options(self, args):
        for option in self.get_possible_options():
            if not option in self.kwargs and hasattr(args, option):
                self.kwargs[option] = getattr(args, option)

    def get_possible_options(self):
        all_options = get_kwargs(self.data_provider)
        all_options.pop("language", None)
        return all_options

    def get(self):
        """Will create a generator of the data returned by function in a module
        the generator will return for each value in the returned data,
            a dictionary with keys, column_names with and added column language
        the len(column_names) < number of 'columns' returend bz the function
        the function can return any iterable of single-values, lists, tuples, dicts
        """
        def run(language):
            for item in self.data_provider(language, **self.kwargs):
                if isinstance(item, dict):
                    assert len(set(self.column_names) - set(item.keys())) >= -1
                    row = {key.lower(): item[key] for key in self.column_names}
                elif isinstance(item, (list, tuple)):
                    sql_column_names = (x.lower() for x in self.column_names)
                    row = dict(itertools.izip(sql_column_names, item))
                elif isinstance(item, (int, basestring)):
                    assert len(self.column_names) == 1
                    row = {self.column_names[0].lower(): item}
                else:
                    assert all(hasattr(item, name) for name in self.column_names)
                    row = {name.lower(): getattr(item, name)
                           for name in self.column_names}
                row['language'] = language
                for key, value in row.items():
                    if isinstance(value, (list, tuple)):
                        assert self.list_modifier
                        row[key] = self.list_modifier(value)
                yield row
        run.buffer_size = self.buffer_size
        return run


class RowGenerators(object):
    row_generators = {
        "phonemes": RowGenerator(
            get_phonemes,
            'get_phonemes',
            ['IPA']),
        "word_frequencies": RowGenerator(
            get_frequent_words,
            'get_frequency_list',
            ['word', 'ranking', 'occurances'],
            extended_return_value=True),
        "pronunciations": RowGenerator(
            get_pronunciation_examples,
            'get_processed_ipas',
            ['word', 'original_pronunciation', 'IPA_pronunciation'],
            list_modifier=','.join,
            buffer_size=10,
            ),
        "pronunciation_examples": RowGenerator(
            get_pronunciation_examples,
            'get_pronunciation_examples',
            ['IPA', 'examples'],
            use_database="only",
            max_words=10000,
            maximum_examples=100,
            list_return_value=True,
            list_modifier=lambda x: x
            ),
        }

    @classmethod
    def get(cls, name, options):
        generator = cls.row_generators[name]
        generator.add_options(options)
        return generator.get()

    @classmethod
    def get_all_options(cls):
        return {key: value.get_possible_options()
                for key, value in cls.row_generators.iteritems()
                }


def get_kwargs(func):
    "Find out the possible kwargs of a function"
    arguments = func.func_code.co_varnames[:func.func_code.co_argcount]
    if func.func_defaults:
        number_of_kwargs = len(func.func_defaults)
        kwargs = arguments[-number_of_kwargs:]
        return dict(zip(kwargs, func.func_defaults))
    else:
        return {}


