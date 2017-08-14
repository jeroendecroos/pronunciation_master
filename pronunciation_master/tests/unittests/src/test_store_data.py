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

    @mock.patch("get_phonemes.get_phonemes", mock.Mock(return_value=[str(x) for x in range(10)]))
    def test_store_phonemes(self):
        # preparing the db
        config_file = self._create_test_config(None)
        db = store_data.create_engine(config_file)
        try:
             store_data._create_superlevel(db)
        except RuntimeError:
             pass
        store_data._create_empty_tables(db, store_data.resources.db_structure)
        # running the store_data
        args = self._get_args()
        args.db_config = config_file
        args.which_table = "phonemes"
        store_data._store_data(args)


class DatabaseTest(StoreDataBaseTest):
    def test_init(self):
        config_file = self._create_test_config()
        store_data.create_engine(config_file)

    @params(('no_tables', {}),
            ('one_table', {'blabla': {'id': {'type': 'Integer'}}}),
            ('two_tables', {
                'first': {'id': {'type': 'Integer'}},
                'second': {'id': {'type': 'Integer'}}
                 }),
            )
    def test_init_database(self, _, structure):
        config_file = self._create_test_config()
        db = store_data.create_engine(config_file)
        with tempfile.NamedTemporaryFile(delete=False) as db_structure_file:
            json.dump(structure, db_structure_file)
        store_data.init_database(db, db_structure_file.name)

    @params(('no_tables', {}),
            ('one_table', {'blabla': {'id': {'type': 'Integer'}}}),
            ('two_tables', {
                'first': {'id': {'type': 'Integer'}},
                'second': {'id': {'type': 'Integer'}}
                 }),
            )
    def test_create_empty_tables(self, _, structure):
        config_file = self._create_test_config(None)
        db = store_data.create_engine(config_file)
        with tempfile.NamedTemporaryFile(delete=False) as db_structure_file:
            json.dump(structure, db_structure_file)
        store_data._create_empty_tables(db, db_structure_file.name)
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
        db = store_data.create_engine(config_file)
        store_data._create_superlevel(db)
        self.execute("CREATE TABLE hello(id int, value varchar(256))", nofetch=True)
        databases = self.execute("SELECT datname FROM pg_database;")
        database_names = set(x[0] for x in databases)
        self.assertTrue(_project_config()['database'] in database_names)

    def test_create_superlevel_failure(self):
        config_file = self._create_test_config(None)
        db = store_data.create_engine(config_file)
        with self.assertRaises(RuntimeError):
            store_data._create_superlevel(db)


class TableTest(StoreDataBaseTest):
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
    def test_from_config(self, _, structure):
        config_file = self._create_test_config(database=None)
        db = store_data.create_engine(config_file)
        table = store_data.Table.from_config("hello", structure, db)
        table.create(db.engine)
        tables = self.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        table_names = set(x[0] for x in tables)
        self.assertTrue("hello" in table_names)

    def test_add_data(self):
        structure = {
            'first': {'type': 'Integer'},
            }
        config_file = self._create_test_config(database=None)
        db = store_data.create_engine(config_file)
        table = store_data.Table.from_config("hello", structure, db)
        table.create(db)
        def iterator():
            for x in range (10):
                 yield {'first': x}
        table.add_data(iterator())
        rows = self.execute("""
            SELECT *
            FROM "hello"
        """)
        self.assertEqual(
            [(x,) for x in range(10)],
            rows,
            )

    def test_from_database(self):
        structure = {
            'first': {'type': 'Integer'},
            'second': {'type': 'Integer'}
            }
        config_file = self._create_test_config(database=None)
        db = store_data.create_engine(config_file)
        table_ref = store_data.Table.from_config("hello", structure, db)
        table_ref.create(db.engine)
        table_target = store_data.Table.from_database("hello", db.engine)
        self.assertEqual(table_ref.name, table_target.name)
        self.assertEqual([x.name for x in table_ref.columns], [x.name for x in table_target.columns])



class RowGeneratorTest(StoreDataBaseTest):
    @params(('one value',
                 (lambda x: x),
                 ['count'],
                 [{'language': 'bla', 'count': x} for x in range(10)]
                 ),
            ('tuple',
                 (lambda x: (x, x**2)),
                 ['count', 'count2'],
                 [{'language': 'bla', 'count': x, 'count2': x**2} for x in range(10)]
                 ),
            ('dict',
                 (lambda x: {'count': x, 'count2': x**2}),
                 ['count', 'count2'],
                 [{'language': 'bla', 'count': x, 'count2': x**2} for x in range(10)]
                 ),
            ('dict_reductor',
                 (lambda x: {'count': x, 'count2': x**2}),
                 ['count'],
                 [{'language': 'bla', 'count': x} for x in range(10)]
                 ),
            )
    def test_one_value(self, _, value_creator, column_names, expected_values):
        class module:  # instead of mock, we mock directly with a class iso module
            @staticmethod
            def function(language):
                for x in range(10):
                    yield value_creator(x)
        gen = store_data._row_generator(module, "function", column_names)
        self.assertEqual(
                [x for x in gen('bla')],
                expected_values
                )
