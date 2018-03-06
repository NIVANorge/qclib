"""
.. moduleauthor: Pierre Jaccard

pyFerry.SiteConfig
==================

This module implements hard coded site specific configuration settings

Variables:
  HOME: contains the name of environment variable pointing to the working 
    directory. 
  EXECUTION_DIR: the content of environment variable defined by `HOME`. This is 
    the directory where the application should run.
  CONFIGURATION_ROOT: top folder containing the configuration files. This folder 
    is given relative to `EXECUTION_DIR`.
  CONFIGURATION_MAIN: name of main configuration file. It should be located 
    under the folder defined by `CONFIGURATION_ROOT`.
  APPLOGGER: name for application logger utility.
  
.. note: if the environment variable defined by `HOME` is not defined, the 
     current directory is used as `EXECUTION_DIR`.
"""

import os

HOME = 'FERRY_HOME'

if HOME in os.environ:
    EXECUTION_DIR = os.environ[HOME]
else:
    EXECUTION_DIR = '.'

if not os.path.isdir(EXECUTION_DIR):
    raise Exception('working directory %s does not exist', EXECUTION_DIR)

CONFIGURATION_ROOT = 'config'
CONFIGURATION_MAIN = 'system.ini'

APPLOGGER = 'FERRYEXE'

