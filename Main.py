"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyRamses.Main
===========================



(C) 21. jan. 2016 Pierre Jaccard
"""

import os

from pyTools import Main as pyMain

from .ConfigManager import sysconf, abspath
from .Loggers import getLogger

LOCKFOLDER = abspath(sysconf['folders']['lock'])

#TIMEOUT     = 86400
TIMEOUT     = -1
LOCKTIMEOUT = 300

log = getLogger(__name__)

class Main(pyMain.Main):
    
    def __init__(self, lockname=None):
        if lockname is not None:
            lockfile = os.path.join(LOCKFOLDER, lockname + '.lock')
        else:
            lockfile = None
        super(Main, self).__init__(lockfile=lockfile, locktimeout=LOCKTIMEOUT, timeout=TIMEOUT)
        return

class Lock(pyMain.Lock):
    pass
    


    
    
