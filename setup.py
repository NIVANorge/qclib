# -*- coding: utf-8 -*-
"""A setuptools based module for the NIVA tsb module/application.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README.md file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='qclib',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.2',

    description="Module containing QC tests",
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/NIVANorge/qclib',

    # Author details
    author='Pierre Jaccard, Elizaveta Protsenko, Zofia Rudjord',
    author_email='pja@niva.no, elizaveta.protsenko@niva.no, zofia.rudjord@niva.no',

    # Choose your license
    license='Owned by NIVA',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Data Access :: Time Series',

        # Pick your license as you wish (should match "license" above)
        'License :: Owned by NIVA http://www.niva.no/',
        
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='data quality tests',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pandas', 'numpy'],
    test_suite='tests',
)
