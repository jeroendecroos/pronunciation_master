import os
import urllib2
import pickle
from bs4 import BeautifulSoup

import codecs

#page_url = "https://nl.wikipedia.org/wiki/Klankinventaris_van_het_Nederlands"
page_url = "https://nl.wikipedia.org/wiki/IPA-notatie_voor_het_Nederlands_en_het_Afrikaans"

with codecs.open('phon_list_wikiNL2.txt','wb','utf8') as outstream:
    print 'extracting %s' % page_url
    page = urllib2.urlopen(page_url).read()
    soup = BeautifulSoup(page, "html.parser")
   
    ### finding all spans.
    spans = soup.findAll('span')

    for span in spans:
        ### check if contains sup + right href
        sup = span.findAll('sup')
        if len(sup) == 1:
              letter = span.contents[0]
              outstream.write(letter[1:-1]+'\n')
