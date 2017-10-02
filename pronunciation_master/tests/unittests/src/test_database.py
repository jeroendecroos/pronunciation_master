import os
import testing.postgresql
import sqlalchemy
import tempfile
import mock
import json
from nose2.tools import params
import psycopg2

from pronunciation_master.tests.testlib import testcase, project_vars
from pronunciation_master.src import database


PASSWORD = 'dog'


def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn(password="None"))
    cursor = conn.cursor()
    cursor.execute("ALTER USER postgres PASSWORD '{}'".format(PASSWORD))
    cursor.close()
    conn.commit()
    conn.close()


Postgresql = testing.postgresql.PostgresqlFactory(
    cache_initialized_db=True,
    on_initialized=handler)


def tearDownModule():
    Postgresql.clear_cache()

def _project_config():
    config_file = os.path.join(project_vars.ASSETS_DIR, 'db_config.test.json')
    with open(config_file) as json_data_file:
        config = json.load(json_data_file)
    return config


class DataBaseTestCase(testcase.BaseTestCase):
    def setUp(self):
        self.postgresql = Postgresql()

    def tearDown(self):
        self.postgresql.stop()

    def _create_test_config(self, database=_project_config()['database']):
        with tempfile.NamedTemporaryFile(delete=False) as json_file:
            config = self.postgresql.dsn()
            if database:
                config['database'] = database
            config['password'] = PASSWORD
            json.dump(config, json_file)
            return json_file.name

    def execute(self, command, nofetch=False):
        conn = psycopg2.connect(**self.postgresql.dsn(password="None"))
        cursor = conn.cursor()
        cursor.execute(command)
        results = None if nofetch else cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return results


class TableTest(DataBaseTestCase):
    def test_init(self):
        database.Table()

    @params(('one column', {
                'first': {'type': 'Integer'}
                }),
            ('two_columns', {
                'first': {'type': 'Integer'},
                'second': {'type': 'Integer'}
                 }),
            ('with String', {
                'first': {'type': 'String'},
                 }),
            )
    def test_from_config(self, _, structure):
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table = database.Table.from_config("hello", {"Columns": structure}, db)
        table.create(db.engine)
        tables = self.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        table_names = set(x[0] for x in tables)
        self.assertTrue("hello" in table_names)

    def test_from_config_no_columns(self):
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        with self.assertRaises(RuntimeError):
            table = database.Table.from_config("hello", {}, db)

    def test_add_data(self):
        def iterator():
            for i in range(10):
                yield {'first': i}
        structure = {
            'first': {'type': 'Integer'},
            }
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table = database.Table.from_config("hello", {'Columns': structure}, db)
        table.create(db)
        table.add_data(iterator())
        rows = self.execute("""
            SELECT *
            FROM "hello"
        """)
        self.assertEqual(
            [(x,) for x in range(10)],
            rows,
            )

    def test_add_data_buffer(self):
        def iterator():
            for i in range(10):
                yield {'first': i}
        structure = {
            'first': {'type': 'Integer'},
            }
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table = database.Table.from_config("hello", {'Columns': structure}, db)
        table.create(db)
        table.add_data(iterator(), buffer_size=10)
        rows = self.execute("""
            SELECT *
            FROM "hello"
        """)
        self.assertEqual(
            [(x,) for x in range(10)],
            rows,
            )

    def test_add_data_no_fail_contains_unique(self):
        def iterator():
            yield {'col1': 0, 'col2': 1, 'col3': 1,}
            yield {'col1': 1, 'col2': 1, 'col3': 2,}
            yield {'col1': 0, 'col2': 1, 'col3': 3,}
            yield {'col1': 2, 'col2': 1, 'col3': 4,}
        structure = {
            'col1': {'type': 'Integer'},
            'col2': {'type': 'Integer'},
            'col3': {'type': 'Integer'},
            }
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table = database.Table.from_config(
            "hello",
            {'Columns': structure,
             'UniqueConstraint': {'name':'something', 'Columns': ['col1', 'col2']},
             },
            db)
        table.create(db)
        table.add_data(iterator())
        rows = self.execute("""
            SELECT col1, col2
            FROM "hello"
        """)
        self.assertEqual(
            [(x, 1,) for x in range(3)],
            rows,
            )

    def test_add_data_fail_unknown_error(self):
        def iterator():
            yield {'col1': 'string'}
        structure = {
            'col1': {'type': 'Integer'},
            }
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table = database.Table.from_config(
            "hello",
            {'Columns': structure,
             },
            db)
        table.create(db)
        class inserter(object):
            def execute(self, *args, **kwargs):
                raise sqlalchemy.exc.IntegrityError("", {}, Exception)
        table.insert = mock.Mock(return_value=inserter())
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            table.add_data(iterator())

    def test_from_database(self):
        structure = {
            'Columns': {
                'first': {'type': 'Integer'},
                'second': {'type': 'Integer'}
                }
            }
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table_ref = database.Table.from_config("hello", structure, db)
        table_ref.create(db.engine)
        table_target = database.Table.from_database("hello", db.engine)
        self.assertEqual(table_ref.name, table_target.name)
        self.assertEqual(
            [x.name for x in table_ref.columns],
            [x.name for x in table_target.columns])


class TableGetDataTest(DataBaseTestCase):

    def create_table(self):
        structure = {
            'number': {'type': 'Integer'},
            'name': {'type': 'String'},
            }
        config_file = self._create_test_config(database=None)
        db = database.create_engine(config_file)
        table = database.Table.from_config("hello", {'Columns': structure}, db)
        table.create(db)
        self.init_data = [{'number': i,
                      'name': 'oneven' if i%2 else 'even',
                      }
                     for i in range(10)]
        table.add_data(self.init_data)
        return table


    def test_get_all(self):
        table = self.create_table()
        results = table.get_data()
        self.assertItemsEqual(
            [dict(x) for x in results],
            self.init_data
            )

    @params(
            ("one", {'name':'even'}),
            ("two", {'name':'even', 'number': 3}),
            )
    def test_get_with_constraint(self, _, constraints):
        table = self.create_table()
        results = table.get_data(specifications=constraints)
        expected = [d for d in self.init_data
                    if all(d[k] == v for k, v in constraints.iteritems())]
        self.assertItemsEqual(
            [dict(x) for x in results],
            expected
            )

    def test_get_with_column(self):
        table = self.create_table()
        results = table.get_data(column='number')
        expected = [d['number'] for d in self.init_data]
        self.assertItemsEqual(
            results,
            expected
            )

    def test_get_with_ordering(self):
        table = self.create_table()
        results = table.get_data(order_by='name')
        expected = [d for d in self.init_data if d['name']=='even']
        expected += [d for d in self.init_data if d['name']=='oneven']
        self.assertItemsEqual(
            [dict(x) for x in results],
            expected
            )

class DatabaseTest(DataBaseTestCase):
    def test_init(self):
        config_file = self._create_test_config()
        database.create_engine(config_file)

    @params(('no_tables', {}),
            ('one_table', {'blabla': {'Columns': {'id': {'type': 'Integer'}}}}),
            ('two_tables', {
                'first': {'Columns':{'id': {'type': 'Integer'}}},
                'second': {'Columns':{'id': {'type': 'Integer'}}}
                 }),
            )
    def test_init_database(self, _, structure):
        config_file = self._create_test_config()
        db = database.create_engine(config_file)
        with tempfile.NamedTemporaryFile(delete=False) as db_structure_file:
            json.dump(structure, db_structure_file)
        database.init_database(db, db_structure_file.name)

    @params(('no_tables', {}),
            ('one_table', {'blabla': {'Columns': {'id': {'type': 'Integer'}}}}),
            ('two_tables', {
                'first': {'Columns':{'id': {'type': 'Integer'}}},
                'second': {'Columns':{'id': {'type': 'Integer'}}}
                 }),
            )
    def test_create_empty_tables(self, _, structure):
        config_file = self._create_test_config(None)
        db = database.create_engine(config_file)
        with tempfile.NamedTemporaryFile(delete=False) as db_structure_file:
            json.dump(structure, db_structure_file)
        database._create_empty_tables(db, db_structure_file.name)
        tables = self.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        table_names = set(x[0] for x in tables)
        for table_name in structure:
            self.assertTrue(table_name in table_names)

    def test_create_empty_tables_noconfig(self):
        config_file = self._create_test_config(None)
        db = database.create_engine(config_file)
        structure = {'table': {}}
        with tempfile.NamedTemporaryFile(delete=False) as db_structure_file:
            json.dump(structure, db_structure_file)
        with self.assertRaises(RuntimeError):
            database._create_empty_tables(db, db_structure_file.name)

    def test_create_superlevel(self):
        config_file = self._create_test_config()
        db = database.create_engine(config_file)
        database._create_superlevel(db)
        self.execute(
            "CREATE TABLE hello(id int, value varchar(256))",
            nofetch=True)
        databases = self.execute("SELECT datname FROM pg_database;")
        database_names = set(x[0] for x in databases)
        self.assertTrue(_project_config()['database'] in database_names)

    def test_create_superlevel_failure(self):
        config_file = self._create_test_config(None)
        db = database.create_engine(config_file)
        with self.assertRaises(RuntimeError):
            database._create_superlevel(db)
