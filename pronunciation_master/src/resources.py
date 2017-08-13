import os

PACKAGEDIR = os.path.dirname(os.path.dirname(__file__))
DATADIR = '{}/data/'.format(PACKAGEDIR)
hermit_dave_github = "https://raw.github.com/hermitdave/FrequencyWords/master/content/2016/" # noqa
phoible_database = "{}/phoible-by-phoneme.tsv".format(DATADIR)
db_config = '{}/db_config.json'.format(DATADIR)
db_structure = '{}/db_structure.json'.format(DATADIR)
