import sys
import codecs
import re

phone_file  = sys.argv[1]
output_dict = sys.argv[2]
freq_list = sys.argv[3]

with codecs.open(phone_file, 'rb','utf8') as instream:
  phonelist = [x.strip() for x in instream]


if len(sys.argv) > 4:
  n = int(sys.argv[4])
else: 
  n = 2 


w_dict = {}
with codecs.open(output_dict, 'rb','utf8') as instream:
  for line in instream:
    key = line.split('[')[0].strip()
    values = eval('['+''.join(line.split('[')[1:]))
    w_dict[key] = values
with codecs.open(freq_list, 'rb' , 'utf8') as instream:
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
