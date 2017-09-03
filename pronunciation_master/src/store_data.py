import json
import sqlalchemy
import sqlalchemy_utils
import itertools

import commandline
import resources
import get_frequent_words
import get_phonemes
import get_pronunciations
import get_pronunciation_examples


def _load_json(filepath):
    with open(filepath) as json_data_file:
        return json.load(json_data_file)


##########################################
#
# BEGIN databasemethods
#
#########################################


def create_engine(config_file):
    config = _load_json(config_file)
    '''Returns a connection and a metadata object'''
    connection_template = "postgresql://{user}:{password}@{host}:{port}/{database}"
    connection_url = connection_template.format(
         **config
    )
    return sqlalchemy.create_engine(connection_url, client_encoding='utf8')


def init_database(db, db_structure_file):
    _create_superlevel(db)
    _create_empty_tables(db, db_structure_file)


def _create_superlevel(db):
    if not sqlalchemy_utils.database_exists(db.url):
        sqlalchemy_utils.create_database(db.url)
    else:
        message = "database '{}' already exists"
        raise RuntimeError(message.format(db.url))


def _create_empty_tables(db, db_structure_file):
    db_structure = _load_json(db_structure_file)
    for table_name, config in db_structure.iteritems():
        table = Table.from_config(
            table_name,
            config,
            db,
            )
        table.create(db)


##########################################
#
# END database methods
#
#########################################


class Table(sqlalchemy.Table):
    @classmethod
    def from_config(cls, table_name, config, engine):
        metadata = sqlalchemy.MetaData(bind=engine)
        cls._set_column_types(config)
        colums = (sqlalchemy.Column(
                     key,
                     values['type'],
                     **values["kwargs"]
                     )
                 for key, values in config.iteritems())
        self = cls(
            table_name,
            metadata,
            *colums
            )
        return self

    @classmethod
    def from_database(cls, table_name, engine):
        meta = sqlalchemy.MetaData(bind=engine)
        return cls(table_name, meta, autoload=True)

    @staticmethod
    def _set_column_types(columns):
        from sqlalchemy import Integer, String  # flake8: noqa
        for key, values in columns.iteritems():
            assert isinstance(values['type'], basestring)
            values['type'] = eval(values['type'])
            values.setdefault('kwargs', {})

    def add_data(self, iterator, buffer=None):
        inserter = self.insert()
        if not buffer:
            inserter.execute(*iterator),
        else:
            rows = []
            for i, row in enumerate(iterator):
                rows.append(row)
                if not (i+1) % buffer:
                    i.execute(*rows)


def _row_generator(module, function, column_names, list_modifier=None, **kwargs):
    """Will create a generator of the data returned by function in a module
    the generator will return for each value in the returned data,
        a dictionary with keys, column_names with and added column language
    the len(column_names) < number of 'columns' returend bz the function
    the function can return any iterable of single-values, lists, tuples, dicts
    """
    def run(language):
        data_provider = getattr(module, function)
        for item in data_provider(language, **kwargs):
            if isinstance(item, dict):
                assert len(set(column_names) - set(item.keys())) >= -1
                row = {key.lower(): item[key] for key in column_names}
            elif isinstance(item, (list, tuple)):
                sql_column_names = (x.lower() for x in column_names)
                row = dict(itertools.izip(sql_column_names, item))
            elif isinstance(item, (int, basestring)):
                assert len(column_names) == 1
                row = {column_names[0].lower(): item}
            else:
                assert all(hasattr(item, name) for name in column_names)
                row = {name.lower(): getattr(item, name)
                       for name in column_names}
            row['language'] = language
            for key, value in row.items():
                if isinstance(value, (list, tuple)):
                    assert list_modifier
                    row[key] = list_modifier(value)

            yield row
    return run


def _store_data(args):
    database = create_engine(args.db_config)
    if args.which_table == 'create_empty':
        init_database(database, resources.db_structure)
    else:
        row_generators = {
            "phonemes": _row_generator(
                get_phonemes,
                'get_phonemes',
                ['IPA']),
            "word_frequencies": _row_generator(
                get_frequent_words,
                'get_frequency_list',
                ['word', 'ranking', 'occurances'],
                extended_return_value=True),
            "pronunciations": _row_generator(
                get_pronunciation_examples,
                'get_processed_ipas',
                ['word', 'original_pronunciation', 'IPA_pronunciation'],
                list_modifier=','.join,
                ),
            }
        table = Table.from_database(args.which_table, database)
        row_generator = row_generators[args.which_table](args.language)
        table.add_data(row_generator)


if __name__ == '__main__':
    description = 'Store different produced data in a database'
    args = commandline.LanguageDatabaseInput.parse_arguments(description)
    _store_data(args)
