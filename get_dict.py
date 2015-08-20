import urllib2
from bs4 import BeautifulSoup

import codecs

src = "http://www.dbnl.org/tekst/paar001abnu01_01/paar001abnu01_01_00%d.php#10"


word_dicts  = {}
for x in range(10,36):
    n_url = src % x
    print 'downloading', n_url
    page = urllib2.urlopen(n_url)
    soup = BeautifulSoup(page.read(), "html.parser")

    divs = soup.findAll("div", {"class":"contentholder"} ) 
    tables = []
    for div in divs:
        tables += div.findAll('table')  
    
    pairs = []
    for x in tables:
        tr = x.findAll('tr')
        for t in tr:
            pairs.append(t.findAll('td'))

    for p in pairs:
        try: 
          key =  p[0].get_text().strip()
          values =  p[1].get_text().strip().split(';')
          word_dicts[key]= values
        except Exception as e:
          print e
with codecs.open('output_dict.txt','wb','utf8') as outstream:
    outstream.write(repr(word_dicts))
