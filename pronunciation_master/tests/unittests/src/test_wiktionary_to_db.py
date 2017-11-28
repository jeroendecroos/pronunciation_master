import unittest

import mock
from mongomock import MongoClient
from nose2.tools import params
import xml
import StringIO

from pronunciation_master.tests.testlib import testcase
from pronunciation_master.src import wiktionary_to_db


stupid_xml = StringIO.StringIO("""<?xml version="1.0"?>
    <address-book>
        <name>Fred Fox</name>
        <phone>1234567</phone>
        <address type="postal">PO Box 987, Anytown, EV</address>
        <address type="street">34 Main St, Anytown, EV</address>
     </address-book>
""")

class ProcessDbTest(testcase.BaseTestCase):
    def setUp(self):
        self.client = MongoClient()
        self.db = getattr(self.client, 'pronunciation_test')
        self.collection = self.db.wiktionary_raw

    def test_init(self):
        handler = wiktionary_to_db.ABContentHandler(self.collection)

    def test_parse_nothing(self):
        stupid_xml = StringIO.StringIO("""<?xml version="1.0"?>
            <something>
             </something>
        """)
        handler = wiktionary_to_db.ABContentHandler(self.collection)
        xml.sax.parse(stupid_xml, handler)

    def test_parse_title(self):
        stupid_xml = StringIO.StringIO("""<?xml version="1.0"?>
            <title>biba
             </title>
        """)
        handler = wiktionary_to_db.ABContentHandler(self.collection)
        xml.sax.parse(stupid_xml, handler)

    def test_parse_text(self):
        stupid_xml = StringIO.StringIO("""<?xml version="1.0"?>
            <title>biba
            <text>lila
             </text>
             </title>
        """)
        handler = wiktionary_to_db.ABContentHandler(self.collection)
        xml.sax.parse(stupid_xml, handler)
        ret = self.collection.find_one()
        self.assertEqual(ret['title'], 'biba')
        self.assertEqual(ret['text'].strip(), 'lila')

