import argparse
import xml.sax
import codecs

import mongodb


class ABContentHandler(xml.sax.ContentHandler):
    def __init__(self, collection=None):
        xml.sax.ContentHandler.__init__(self)
        self._text = False
        self._word = False
        self._buffer = []
        self._table = collection

    def startElement(self, name, attrs):
        if name == 'title':
            self._word = True
        elif name == 'text':
            self._text = True

    def endElement(self, name):
        if name == 'text':
            if self._text and self._word:
                self._print_buffer()
                self._reset()

    def _reset(self):
        self._text = False
        self._word = False
        self._buffer = []

    def characters(self, content):
        if self._word is True:
            self._word = content
        elif self._text is True and self._word:
            self._buffer.append(content)

    def _print_buffer(self):
        if self._table:
            entry = {
                'title': self._word.encode('utf-8'),
                'text': ''.join(self._buffer).encode('utf-8'),
            }
            self._table.insert_one(entry)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wiktionary')
    parser.add_argument('--database', required=True)
    args = parser.parse_args()
    collection = mongodb.default_local_db(
        args.database,
        drop_collection='wiktionary_raw'
        ).wiktionary_raw
    with codecs.open(args.wiktionary, 'rb') as f:
        xml.sax.parse(f, ABContentHandler(collection))
