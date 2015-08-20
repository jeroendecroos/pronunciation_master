import codecs
import urllib2
from bs4 import BeautifulSoup

n_url = "http://wortschatz.uni-leipzig.de/Papers/top10000nl.txt"

page = urllib2.urlopen(n_url)
soup = BeautifulSoup(page.read(), "html.parser")

l = soup.get_text()
words = l.split('\n')
with codecs.open('freq_list.out.txt', 'wb', 'utf8') as outstream:
  checked_w = []
  for w in words:
    if w.strip():
      w_l = w.lower()
      if w_l not in checked_w:
        checked_w.append(w_l)
        outstream.write(w_l+'\n')
