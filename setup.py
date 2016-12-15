from setuptools import setup, find_packages

#to use a consistent encoding
from codecs import open
import os

def _lint():
    """Run lint and return an exit code."""
    project_python_files = [filename for filename in get_project_files()
                            if filename.endswith(b'.py')]
    retcode = subprocess.call(
        ['flake8', '--max-complexity=10'] + project_python_files)
    if retcode == 0:
        print_success_message('No style errors')
    return retcode



here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup_dict = dict(
    # general information
    name='pronunciation_master',
    version='0.1.0',
    description='helps improving pronunciation of a language',
    long_description="""various tools to help with learning the pronunciation of a language.
    some examples are: getting all the phonemes of a language, get the pronunciation of a word, get examples for each phoneme, ...
    """,

    # useful information
    url='https://github.com/jeroendecroos/pronunciation_master',
    author='Jeroen Decroos',
    author_email='jeroen.decroos+github@gmail.com',
    license='GNU General Public License v3 (GPLv3)',

    # usage information
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education :: Testing',
        ],
    keywords='pronunciation language learning phonemes',

    # package details
    packages=find_packages(exclude=['tests*']),
    install_requires=[],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)

def main():
    setup(**setup_dict)


if __name__ == '__main__':
    main()
