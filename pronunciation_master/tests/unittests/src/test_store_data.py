from nose2.tools import params
import mock
import json
import psycopg2
import tempfile
import testing.postgresql
import unittest

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import store_data


PASSWORD = 'dog'

def _project_config():
    config_file = store_data.resources.db_config
    with open(config_file) as json_data_file:
        config = json.load(json_data_file)
    return config


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


class StoreDataBaseTest(testcase.BaseTestCase):
    def setUp(self):
        self.postgresql = Postgresql()

    def tearDown(self):
        self.postgresql.stop()

    def _create_test_config(self, database=_project_config()['database']):
        with tempfile.NamedTemporaryFile(delete=False) as json_file:
            config = self.postgresql.dsn()
            if database:
                config['database']= database
            config['password']= PASSWORD
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


class StoreDataTest(StoreDataBaseTest):
    def _get_args(self):
        args = mock.Mock()
        args.db_config = self._create_test_config()
        return args

    def test_create_empty(self):
        args = self._get_args()
        args.which_table = "create_empty"
        store_data._store_data(args)


class DatabaseTest(StoreDataTest):
    def test_init(self):
        config_file = self._create_test_config()
        store_data.Database(config_file)

    @params(('no_tables', {}),
            ('one_table', {'blabla': {'id': {'type': 'Integer'}}}),
            ('two_tables', {
                'first': {'id': {'type': 'Integer'}},
                'second': {'id': {'type': 'Integer'}}
                 }),
            )
    @mock.patch("pronunciation_master.src.store_data.Database._create_superlevel")
    def test_create_empty_database(self, _, structure, mock):
        """ currently mocking create superlevel, because can't find the tables in different db with testing.postgresql
        """
        config_file = self._create_test_config(None)
        db = store_data.Database(config_file)
        with tempfile.NamedTemporaryFile(delete=False) as db_structure_file:
            json.dump(structure, db_structure_file)
        db.create_empty_database(db_structure_file.name)
        tables = self.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        table_names = set(x[0] for x in tables)
        for table_name in structure:
            self.assertTrue(table_name in table_names)

    def test_create_superlevel(self):
        config_file = self._create_test_config()
        db = store_data.Database(config_file)
        db._create_superlevel()
        self.execute("CREATE TABLE hello(id int, value varchar(256))", nofetch=True)
        databases = self.execute("SELECT datname FROM pg_database;")
        database_names = set(x[0] for x in databases)
        self.assertTrue(_project_config()['database'] in database_names)

    def test_create_superlevel_failure(self):
        config_file = self._create_test_config(None)
        db = store_data.Database(config_file)
        with self.assertRaises(RuntimeError):
            db._create_superlevel()


class TableTest(StoreDataTest):
    def test_init(self):
        store_data.Table()

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

    def test_from_config(self, _, config):
        store_data.Table.from_config("myname", config)

    @params(('one column', {
                'first': {'type': 'Integer'}
                }),
            ('two_columns', {
                'first': {'type': 'Integer'},
                'second': {'type': 'Integer'}
                 }),
            )

    def test_create_empty_table(self, _, config):
        config_file = self._create_test_config(database=None)
        db = store_data.Database(config_file)
        table = store_data.Table.from_config("hello", config)
        table.create_empty_table(db.engine)
        tables = self.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        table_names = set(x[0] for x in tables)
        self.assertTrue("hello" in table_names)
