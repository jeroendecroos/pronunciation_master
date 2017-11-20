from pronunciation_master.tests.testlib import testcase

import pronunciation_master.src.mongodb as mongodb


class DefaultLocalDbTest(testcase.BaseTestCase):
    def test_basic(self):
        mongodb.default_local_db()
