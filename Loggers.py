"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Loggers
===============

Main loggers used for processign Ferrybox data.

(C) 17. jan. 2016 Pierre Jaccard
"""

import os

from pyTools.LogUtils import Loggers 

from .ConfigManager import sysconf, abspath

LOGFOLDER = abspath(sysconf['folders']['log'])

"""
Variable `LOG` is used to avoid duplicate logging handlers in the logger tree.
It is therefore used to save the root logger and its handlers.
"""
LOG = None

if not os.path.exists(LOGFOLDER):
    os.makedirs(LOGFOLDER)

def getLogger(name=None):
    """
    Get default logger for specified module name. To be typically called at the 
    beginning of a module and define a module wide logger variable::
    
        log = getLogger(__name__)
    
    This function will add sqlite and file logger.  
    """
    l = globals()['LOG']
    if l is not None:
        h = []
    else:
        h = None
    l = Loggers.getSQLiteLogger(name, handlers=h, dbname=os.path.join(LOGFOLDER, 'log.db'))
    if h is None:
        l.addHandler(Loggers.getConsoleHandler())
        try:
            l.addHandler(Loggers.getFileHandler(os.path.join(LOGFOLDER, 'syslog.log')))
        except:
            l.addHandler(Loggers.getFileHandler(os.path.join('.', '_syslog.log')))
    globals()['LOG'] = l
    return(l)
    
LOG = getLogger()




