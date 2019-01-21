# -*- coding: utf-8 -*-
"""A setuptools based module for the NIVA tsb module/application.
"""

from setuptools import setup

setup(
    name='qclib',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.2.1',

    description="Module containing QC tests",

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
        'Development Status :: 0 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Data Access :: Time Series',

        # Pick your license as you wish (should match "license" above)
        'License :: Owned by NIVA http://www.niva.no/',
        
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='data quality tests',
    packages=["."],
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib'
    ],
    extras_require={
      "test": [
          "pytest"
      ]
    },
    test_suite='qc_unittest',
)
