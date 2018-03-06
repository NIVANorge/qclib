"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.netCDF.Data
===========================



(C) 12. okt. 2016 Pierre Jaccard
"""

from .Generic import netCDF
from ..Globals import netCDFGroups

class RawFerrybox(netCDF):
    
    def __init__(self, fnc, **kw):
        super(RawFerrybox, self).__init__(fnc, **kw)
        self._group = netCDFGroups.RAW_FERRYBOX
        return

