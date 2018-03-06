"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.ConfigManager
=====================

Provides package access to the configuration files.

(C) 14. jan. 2016 Pierre Jaccard
"""

import os
from configobj import ConfigObj

from . import SiteConfig

CONFIGROOT = os.path.join(SiteConfig.EXECUTION_DIR, SiteConfig.CONFIGURATION_ROOT)
MAINCONFIG = 'system.ini'

CONFIGFILE = os.path.join(CONFIGROOT, MAINCONFIG)

#if not os.path.exists(CONFIGFILE):
#    raise RuntimeError('missing configuration file')

sysconf = ConfigObj(CONFIGFILE)

def abspath(p):
    """
    Return the absolute path for `p`, a folder relative to the working directory.
    """
    p = os.path.join(SiteConfig.EXECUTION_DIR, p)
    return(p)

def absfolders(*args):
    """
    Generate the absolute paths for the system sub configuration. Arguments are
    the keys to apply recursively to the configuration.
    """ 
    d = sysconf
    for a in args:
        d = d[a]
    absd = dict(map(lambda x: (x,abspath(d[x])), d.keys()))
    return(absd)
