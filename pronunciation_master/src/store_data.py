import json
import sqlalchemy
import sqlalchemy_utils
import psycopg2
from psycopg2 import errorcodes as psycopg2_errorcodes

import commandline
import resources
import data_generators

# Note: This code should be changed to use the sqlaclchemy ORM

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
        if not config:
            raise RuntimeError('table "{}" needs an non empty config'.format(table_name))
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
        if not 'Columns' in config:
            raise RuntimeError('Colums must be present in the structure for {}'.format(table_name))
        metadata = sqlalchemy.MetaData(bind=engine)
        cls._set_column_types(config['Columns'])
        columns = (sqlalchemy.Column(
                     key,
                     values['type'],
                     **values["kwargs"]
                     )
                 for key, values in config['Columns'].iteritems())
        table_config = []
        if 'UniqueConstraint' in config:
            constraints = config['UniqueConstraint']
            table_config.append(sqlalchemy.UniqueConstraint(
                *constraints['Columns'],
                **{k:v for k, v in constraints.iteritems() if k in ['name']}
                ))
        self = cls(
            table_name,
            metadata,
            *(list(columns) + table_config)
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
        """add each row in the iterator to the database
        Will ignore rows that violate unique duplicates
        is also not recommmend for large bulk insertions.
        """
        # WE don't do bulk insertions so we can ignore unique duplicates.
        # Having a proper implimentation with on_conflict is too much work for now
        valid_error_codes = [getattr(psycopg2_errorcodes, x)
                             for x in (
                                 'UNIQUE_VIOLATION',
                                 )
                             ]
        inserter = self.insert()
        for row in iterator:
            try:
                inserter.execute(row),
            except sqlalchemy.exc.IntegrityError as e:
                if isinstance(e.orig, psycopg2.IntegrityError) and e.orig.pgcode in valid_error_codes:
                    print("skipping row '{}' due to error '{}".format(row, e))
                else:
                    raise

def _store_data(args):
    database = create_engine(args.db_config)
    if args.which_table == 'create_empty':
        init_database(database, resources.db_structure)
    else:
        table = Table.from_database(args.which_table, database)
        row_generator = data_generators.RowGenerators.get(args.which_table)
        table.add_data(row_generator(args.language))


if __name__ == '__main__':
    description = 'Store different produced data in a database'
    args = commandline.LanguageDatabaseInput.parse_arguments(description)
    _store_data(args)
