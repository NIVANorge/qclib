# -*- coding: utf-8 -*-
"""A setuptools based module for the NIVA tsb module/application.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# get the version from the __version__.py file
version_dict = {}
with open(path.join(here, 'src', 'qclib', '__version__.py')) as f:
    exec(f.read(), version_dict)

# Get the long description from the README.md file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nivacloud-qclib',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version_dict['__version__'],
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
        #   0 - Alpha
        #   1 - Beta
        #   2 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # 'Topic :: Data Access :: Time Series',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        
        'Programming Language :: Python :: 3',
    ],

    keywords='data quality tests',
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    install_requires=[
        'pandas>=1.1,<2.0',
        'numpy>=1.16,<2.0',
        'pydantic>=1.0,<2.0',
        'matplotlib>=3.0,<4.0'
    ],
    extras_require={
      "test": [
          "pytest"
      ]
    },
    test_suite='tests',
)
