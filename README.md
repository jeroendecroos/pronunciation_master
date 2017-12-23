# pronunciation_master
various tools to help with learning the pronunciation of a language.
some examples are:
    getting all the phonemes of a language,
    get the pronunciation of a word, get examples for each phoneme, ...

Following is some guidelines to get everything to work, in the future this will be automated.

virtualenv
pip install -U pip setuptools
pip install -r requirements.txt


Following is to test with lettuce:
sudo apt-get install mongodb 
sudo apt-get install postgresql
sudo -u postgres psql -c "CREATE USER tester with pass 'XXXXXX'"
sudo -u postgres psql -c "ALTER ROLE tester with CREATEDB LOGIN"

