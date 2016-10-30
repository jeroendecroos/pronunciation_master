try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description', 'A tool to help master the pronunciation of the language.'
    'author': 'Jeroen Decroos',
    'url': '',
    'download_url': '',
    'author_email': 'jeroen.decroos@gmail.com',
    'version': '0.1',
    'install_requires': [],
    'packages': ['pronunciation_examples'],
    'scripts': [],
    'name': 'projectname'
    }

setup(**config)
