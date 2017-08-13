import json
import sqlalchemy
import sqlalchemy_utils

import commandline
import resources


class Database(object):
    def __init__(self, config_file):
        with open(config_file) as json_data_file:
            self._config = json.load(json_data_file)
        self.engine = self._database_engine()

    def create_empty_database(self, db_structure_file):
        with open(db_structure_file) as json_data_file:
            db_structure = json.load(json_data_file)
#        self._create_superlevel()
        self._create_tables(db_structure)

    def _create_superlevel(self):
        if not sqlalchemy_utils.database_exists(self.engine.url):
            sqlalchemy_utils.create_database(self.engine.url)
        else:
            message = "database '{}' already exists"
            raise RuntimeError(message.format(self._config['database']))

    def _create_tables(self, db_structure):
        for table_name, config in db_structure.iteritems():
            table = Table.from_config(
                table_name,
                config,
                )
            table.create_empty_table(self.engine)

    def _database_engine(self):
        '''Returns a connection and a metadata object'''
        connection_template = "postgresql://{user}:{password}@{host}:{port}/{database}"
        connection_url = connection_template.format(
             **self._config
        )
        return sqlalchemy.create_engine(connection_url, client_encoding='utf8')


class Table(object):
    def __init__(self):
        self.name = ""
        self._columns = {}

    @classmethod
    def from_config(cls, table_name, config):
        self = cls()
        self.name = table_name
        self._columns = config
        self._set_column_types()
        return self

    def _set_column_types(self):
        from sqlalchemy import Integer, String
        for key, values in self._columns.iteritems():
            assert isinstance(values['type'], basestring)
            values['type'] = eval(values['type'])
            values.setdefault('kwargs', {})

    def create_empty_table(self, engine):
        metadata = sqlalchemy.MetaData(bind=engine)
        self.table = sqlalchemy.Table(
                self.name,
                metadata,
                *self.columns
                )
        self.table.create(engine)

    @property
    def columns(self):
        return (sqlalchemy.Column(
                    key,
                    values['type'],
                    **values["kwargs"])
                for key, values in self._columns.iteritems())


def _store_data(args):
    if args.which_table == 'create_empty':
        database = Database(args.db_config)
        database.create_empty_database(resources.db_structure)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    description = 'Store phonemes, frequency lists, pronunciations in a database'
    args = commandline.LanguageDatabaseInput.parse_arguments(description)
    _store_data(args)
