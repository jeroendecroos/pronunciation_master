import sys
import codecs

phone  = sys.argv[1]
if len(sys.argv) > 2:
  n = int(sys.argv[2])
else: 
  n = 20 


with codecs.open('output_dict.txt', 'rb','utf8') as instream:
  w_dict = eval(instream.read())
with codecs.open('freq_list.out.txt', 'rb' , 'utf8') as instream:
  f_list = [x.strip() for x in instream]

n_found=0
for f in f_list:
  if f not in w_dict:
     continue
  else:
     pronunciations = w_dict[f]
     found = False
     for x in pronunciations:
        if phone in x:
            found = True
            break
     if found:
           print(f+'\t'+str(pronunciations))
           n_found += 1
     if n_found ==n:
          break
  
