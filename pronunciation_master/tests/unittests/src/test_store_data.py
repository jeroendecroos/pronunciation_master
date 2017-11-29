import json
import mock
import os
import testing.postgresql
import tempfile
import psycopg2

from pronunciation_master.tests.testlib import testcase, project_vars
from pronunciation_master.src import store_data
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


class StoreDataTest(DataBaseTestCase):
    def _get_args(self):
        args = mock.Mock()
        args.db_config = self._create_test_config()
        return args

    def test_create_empty(self):
        args = self._get_args()
        args.which_table = "create_empty"
        store_data._store_data(args)

    def _prepare_db(self):
        self.config_file = self._create_test_config(None)
        db = database.create_engine(self.config_file)
        try:
            database._create_superlevel(db)
        except RuntimeError:
            pass
        database._create_empty_tables(db, store_data.resources.db_structure)

    @mock.patch(
        "pronunciation_master.src.get_phonemes.get_phonemes",
        mock.Mock(return_value=[str(x) for x in range(10)])
        )
    def test_store_phonemes(self):
        self._prepare_db()
        self._run_store_data("phonemes")

    def _run_store_data(self, which_table):
        args = self._get_args()
        args.db_config = self.config_file
        args.which_table = which_table
        args.language = 'dutch'
        store_data._store_data(args)
