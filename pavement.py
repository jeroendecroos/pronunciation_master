import os
import subprocess
from codecs import open
from setuptools import find_packages

from paver.easy import options, task
from distutils import spawn

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup_dict = dict(
    # general information
    name='pronunciation_master',
    version='0.1.0',
    description='helps improving pronunciation of a language',
    long_description=long_description,

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

options(setup=setup_dict)


@task
def lint():
    # This refuses to format properly when running `paver help' unless
    # this ugliness is used.
    ('Perform PEP8 style check, run PyFlakes, and run McCabe complexity '
     'metrics on the code.')
    project_python_files = [filename for filename in get_project_files()
                            if filename.endswith(b'.py')]
#    print ' '.join(['flake8', '--max-complexity=10'] + project_python_files)
    retcode = subprocess.call(
        ['flake8', '--max-complexity=10'] + project_python_files)
    if retcode == 0:
        print('No style errors')
    raise SystemExit(retcode)


def get_project_files():
    """Retrieve a list of project files, ignoring hidden files.

    :return: sorted list of project files
    :rtype: :class:`list`
    """
    if is_git_project() and has_git():
        return get_git_project_files()
    else:
        raise RuntimeError('only works with git')


def is_git_project():
    return os.path.isdir('.git')


def has_git():
    return bool(spawn.find_executable("git"))


def get_git_project_files():
    """Retrieve a list of all non-ignored files, including untracked files,
    excluding deleted files.

    :return sorted list of git project files
    """
    cached_and_untracked_files = git_ls_files(
        '--cached',  # All files cached in the index
        # Exclude untracked files that would be excluded by .gitignore, etc.
        '--exclude-standard')
    uncommitted_deleted_files = git_ls_files('--deleted')
    # Since sorting of files in a set is arbitrary, return a sorted list to
    # provide a well-defined order to tools like flake8, etc.
    return sorted(cached_and_untracked_files - uncommitted_deleted_files)


def git_ls_files(*cmd_args):
    """Run ``git ls-files`` in the top-level project directory. Arguments go
    directly to execution call.

    return set of file names
    """
    cmd = ['git', 'ls-files']
    cmd.extend(cmd_args)
    return set(subprocess.check_output(cmd).splitlines())
