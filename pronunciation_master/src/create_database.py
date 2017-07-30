from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

# and has CREATE DATABASE permissions, rather than use a superuser.
DB_CONFIG_DICT = {
    'user': 'creator',
    'password': '1_pw_t_c_db',
    'host': 'localhost',
    'port': 5432,
}

DB_CONN_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{database}"

DB_CONN_URI_DEFAULT = (DB_CONN_FORMAT.format(
    database='pronunciation_master',
    **DB_CONFIG_DICT
))

database_name = 'pronunciation_master'
engine = create_engine(DB_CONN_URI_DEFAULT)

if not database_exists(engine.url):
        create_database(engine.url)

        print(database_exists(engine.url))
else:
    print "database exists"
