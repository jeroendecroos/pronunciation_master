from pronunciation_master.tests.testlib import testcase

import pronunciation_master.src.mongodb as mongodb

import uuid


class DefaultLocalDbTest(testcase.BaseTestCase):
    def test_basic(self):
        mongodb.default_local_db()

    def test_specify(self):
        mongodb.default_local_db(database='randomdb')

    def test_drop(self):
        collection = 'randomdb'+str(uuid.uuid4())
        db = mongodb.default_local_db()
        getattr(db, collection).insert_one({'ba': 'ha'})
        db = mongodb.default_local_db(drop_collection=collection)
        self.assertEqual(getattr(db, collection).find_one(), None)

    def test_no_drop(self):
        collection = 'randomdb'+str(uuid.uuid4())
        db = mongodb.default_local_db()
        getattr(db, collection).insert_one({'ba': 'ha'})
        db = mongodb.default_local_db()
        self.assertEqual(getattr(db, collection).find_one()['ba'], 'ha')
