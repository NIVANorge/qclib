"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Types
===========================



(C) 28. jun. 2016 Pierre Jaccard
"""

import datetime
import numpy as np

def datetimeFunction(fmt):
    def f(x):
        t = datetime.datetime.strptime(x, fmt)
        return(t)
    return(f)

def dateFunction(fmt):
    def f(x):
        t = datetime.datetime.strptime(x, fmt)
        return(t)
    return(f)

def timeFunction(fmt):
    def f(x):
        t = datetime.datetime.strptime(x, fmt)
        t = t.time()
        t = t.hour*3600.0 + t.minute*60.0 + t.second + t.microsecond/10**6
        t = t/86400.0
        return(t)
    return(f)

def boolFunction(threshold=None):
    def f(x):
        if threshold is None:
            x = np.uint8(round(np.float64(x)))
        else:
            x = np.uint8(round(np.float64(x)) > threshold)
        return(x)
    return(f)


def stringFunction():
    def f(s):
        ii = range(len(s))
        d  = map(lambda x: np.uint8(int(s[x], base=16)), ii)
        d  = np.uint8(d, dtype=np.uint8)
        return(d)
    return(f)
        
