# pronunciation_master
various tools to help with learning the pronunciation of a language.
some examples are:
    getting all the phonemes of a language,
    get the pronunciation of a word, get examples for each phoneme, ...

Following is some guidelines to get everything to work, in the future this will be automated.

virtualenv
pip install -U pip setuptools
pip install -r requirements.txt


install postgresql

following is to test with lettuce a test postgresql installation would be better.
But working in a virtualbox that is set up quikly and independent from production is good enough for the moment
CREATE USER tester with pass 'XXXXXX'
ALTER ROLE tester with CREATEDB

