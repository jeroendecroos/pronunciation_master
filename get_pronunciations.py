import sys
import codecs
import re

phone_file  = sys.argv[1]

with codecs.open(phone_file, 'rb','utf8') as instream:
  phonelist = eval(instream.read())


if len(sys.argv) > 2:
  n = int(sys.argv[2])
else: 
  n = 20 


with codecs.open('output_dict.txt', 'rb','utf8') as instream:
  w_dict = eval(instream.read())
with codecs.open('freq_list.out.txt', 'rb' , 'utf8') as instream:
  f_list = [x.strip() for x in instream]

for w,ps in w_dict.iteritems():
   for pn in range(len(ps)):
       ps[pn] =re.sub('\(.*','', ps[pn])

def find_examples(phone):
  n_found=0
  for f in f_list:
    if f not in w_dict:
       continue
    else:
       pronunciations = w_dict[f]
       found = False
       for x in pronunciations:
          if re.search(phone,x):
              found = True
              break
       if found:
             print(f+'\t' + ' , '.join(pronunciations))
             n_found += 1
       if n_found ==n:
            break

for x in phonelist:
  print '\n'
  print x
  find_examples(x)    
