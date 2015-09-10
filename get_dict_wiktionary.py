import os
import urllib2
import pickle
from bs4 import BeautifulSoup

import codecs

#page_url = "https://nl.wiktionary.org/w/index.php?title=Categorie:Woorden_in_het_Nederlands&from=A"
page_url = "https://nl.wiktionary.org/w/index.php?title=Categorie:Woorden_in_het_Nederlands&subcatfrom=A&filefrom=A&pageuntil=%27s-Gravenhaags#mw-pages"
#page_url = "https://nl.wiktionary.org/w/index.php?title=Categorie:Woorden_in_het_Nederlands&from=%C3%9C"

refs = []
c = 0
while page_url:
    break   ###TEMP
    print 'downloading', page_url

    page = urllib2.urlopen(page_url)
    soup = BeautifulSoup(page.read(), "html.parser")

    dv = soup.findAll('div',{'id':'mw-pages'})
    if len(dv) != 1:
         raise Exception('zero; two or more div:mw-pages')

    #### Getting word refs
    divs = dv[0].findAll("div", {"class":"mw-category-group"} ) 
    if not divs:
         raise Exception('zero div:mw-category-group')
    for div in divs:
      asses = div.findAll('a', href=True)
      refs += [a['href'] for a in asses]
              
    #### getting next page
    dv = soup.findAll('div',{'id':'mw-pages'})
    np = dv[0].findAll('a', recursive=False)
    page_url = ""
    for p in np:
        if p.contents[0] == u'volgende pagina':
             page_url = 'https://nl.wiktionary.org/' + p['href']
             break
    c += 1
    print c

#### TEMP
with codecs.open('output_dict_wikiNL.txt','rb','utf8') as instream:
    for x in instream:
        refs.append(x.strip())      
####TEMP
#refs=['/wiki/%3D/Hua']
with codecs.open('output_dict_wikiNL2.txt','wb','utf8') as outstream:
  for x in refs:
    if x.count('/') != 2:
         print 'skipping', x
         continue
    page_url =  'https://nl.wiktionary.org'+x
    print 'extracting %s' % page_url
#    page = urllib2.urlopen(page_url).read()

#    with open(os.getcwd()+x, 'wb') as outstream:
#        pickle.dump(page, outstream)
#    continue
    with open(os.getcwd()+x,'rb') as instream:
        page = pickle.load(instream)
    

    soup = BeautifulSoup(page, "html.parser")
   
    ### finding word
    header = soup.findAll('h1',{'id':'firstHeading', 'class':'firstHeading'})[0].text


    ### finding pronunciation
    dv = soup.findAll('div',{'id':'mw-content-text'})
    if len(dv) != 1:
         raise Exception('zero; two or more div:mw-pages')
    h2s = dv[0].findAll('h2', recursive=False)
    h2_nl = None    
#    print '\t Looking for h2 with %s' % 'Nederlands'
    for h2 in h2s:
        as_in_h2 = h2.findAll('a')
        if len(as_in_h2) != 1:
            raise Exception('zero; two or more a in h2')
        if as_in_h2[0].contents[0] == u'Nederlands':
            h2_nl = h2
            break
    if not h2_nl:
         print "\tdidn't found Nederlds"
         continue     
    

#    print '\t Looking for uitspraken'
    uitspraken = [] 
    next = h2_nl.nextSibling
    while next and next.name != "h2":
#        print next
        if type(next) != type(h2):
            next=next.nextSibling
            continue
        sp = next.findAll('span',{'id':'Uitspraak'})
        if sp:
            sp = sp[0]
            lis = None
            while not lis and next.nextSibling:
               next = next.nextSibling
#               print next 
               if type(next) == type(h2):   ### not just text, 'tag'like stuff 
                   lis = next.findAll('li') 
               if lis:
                 for li in lis:
                   if li.findAll('a') and li.findAll('a')[0].contents[0] == 'IPA':
                     fonts = li.findAll('font')
                     uitspraken = [f.contents[0] for f in fonts]
               else:
                 lis=None
            break
        next = next.nextSibling
    if uitspraken:
        print '\t\t'+str(uitspraken) + '\t'+header
        outstream.write(header+'\t'+repr(uitspraken)+'\n')
    else:
          print '\t\tnotfound:'+header
