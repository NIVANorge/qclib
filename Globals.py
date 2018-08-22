"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Globals
===============

Provides package access to Global variables

(C) 14. jan. 2016 Pierre Jaccard
"""

from .Error import Error

FolderMetaFile = 'meta.ini' 
FolderLogFile  = 'syslog.log'

CATEGORIES = ('provider', 'platform')

MD5_DATA_NAME = 'md5'

D_FORMAT_USR  = '%Y-%m-%d' 
DT_FORMAT_USR = '%Y-%m-%d %H:%M:%S'
DT_FORMAT_ISO = '%Y%m%dT%H%M%SZ'

class FileStatus:
    NEW_RAW_DATA_         = 'NEW_RAW_DATA_'
    NEW_RAW_DATA_FERRYBOX = 'NEW_RAW_DATA_FERRYBOX'
    NEW_RAW_DATA_PCO2     = 'NEW_RAW_DATA_PCO2'
    NEW_NAV_DATA          = 'NEW_NAV_DATA'
    NEW_RTQC_FLAGS        = 'NEW_RTQC_FLAGS'
    SSRDV_EXTRACTED       = 'SSRDV_EXTRACTED'
    JERICO_EXTRACTED      = 'JERICO_EXTRACTED'
    IOF_EXTRACTED         = 'IOF_EXTRACTED'
    NEW_PORT_EVENTS       = 'NEW_PORT_EVENTS'
    NEW_TRANSECTS         = 'NEW_TRANSECTS'
    
class Operations:
    ADD_RAW_DATA_         = 'ADD_RAW_DATA_'
    ADD_RAW_DATA_FERRYBOX = 'ADD_RAW_DATA_FERRYBOX'
    ADD_RAW_DATA_PCO2     = 'ADD_RAW_DATA_PCO2'
    COMBINE_RAW_DATA_     = 'COMBINE_RAW_DATA_' 
    COMBINE_RAW_DATA_PCO2 = 'COMBINE_RAW_DATA_PCO2' 
    UPDATE_NAVIGATION     = 'ADD_NAVIGATION'
    APPLY_RTQC            = 'APPLY_RTQC'
    EXTRACT_SSRDV         = 'EXTRACT_SSRDV'
    EXTRACT_JERICO        = 'EXTRACT_JERICO'
    EXTRACT_IOF           = 'EXTRACT_IndreOsloFjord'
    SCAN_FOR_PORT_EVENTS  = 'SCAN_FOR_PORT_EVENTS'       
    SCAN_FOR_TRANSECTS    = 'SCAN_FOR_TRANSECTS'
    EXTRACT_CMEMS         = 'EXTRACT_CMEMS'
  
class EventTypes:
    UNKNOWN   = 'NA'
    DEPARTURE = 'DEPARTURE'
    ARRIVAL   = 'ARRIVAL'
    IGNORED   = 'IGNORED_EVENT'
    
class netCDFGroups:
    RAW_FERRYBOX = '/raw/ferrybox'
    
class SQLTransformations:
    
    SCALE = 10000
    
    @classmethod
    def pos2sql(cls, pos):
        sql = int(round(pos * cls.SCALE))
        return(sql)

    @classmethod
    def sql2pos(cls, sql):
        pos = sql/cls.SCALE
        return(pos)
    
class Areas:
    Baltic = {
        'lat': (53.5, 62.0, 66.0, 66.0, 53.5), 
        'lon': (10.0, 10.0, 20.0, 30.0, 30.0)
        }
    NorthWestShelf = {
        'lat': ( 48,  68, 68, 48),
        'lon': (-30, -30, 15, 15) 
        }
    Arctic = {
        'lat': (  67,   89,  89,  67), 
        'lon': (-180, -180, 180, 180)
        }
    Iberic = {
        'lat': ( 30.0,  48.0, 48.0, 42.0, 40.0, 30.0),   
        'lon': (-30.0, -30.0,  0.0,  0.0, -5.5, -5.5)
        }
    MedSea = {
        'lat': (30.0, 40.0, 46.0, 46.0, 40.25, 40.25, 30.0), 
        'lon': (-5.5, -5.5,  5.0, 20.0, 26.60, 36.50, 36.5)
        }
    BlackSea = {
        'lat': (40.0, 40, 48, 48.0), 
        'lon': (26.5, 42, 42, 26.5)
        }
    Biscay = {
        'lat': (42,  48, 48,  42),  
        'lon': (-9,  -9,  0,   0)  
        }
    WesternGulfFinland = {
        'lat': (59.45, 59.45, 60.30, 60.30),
        'lon': (23.22, 30.20, 30.20, 23.22)
        }
    SouthernBalticProper = {
        'lat': (54.52, 54.52, 56.20, 56.20),
        'lon': (12.27, 17.09, 17.09, 12.27)
        }
    NorthernBalticProper = {
        'lat': (58.36, 58.36, 59.62, 59.62),
        'lon': (19.88, 23.21, 23.21, 19.88)
        }
    
    
    
if False:
    
    
    
    
    POOLCATEGORIES = ('provider', 'platform', 'year')
    
    INSTALLATIONS_HEADER = ('ship', 'day', 'hour', 'par:Ed', 'dev:Ed', 
                            'par:Ld', 'dev:Ld', 'iza:Ld', 'iaa:Ld',
                            'par:Lu', 'dev:Lu', 'iza:Lu', 'iaa:Lu',
                            'par:UV', 'dev:UV')
    
    class NotAnError(Error): pass
    
    VERSIONS_TO_KEEP = 10
    
    PI_NAME = 'Kai Sorensen'
    
    
    # MERIS Wavelengths                                                                                                       
    MERIS_WLEN = [ 412, 443, 490, 510, 560, 620, 665, 681, 709, 753, 778, 865, 885 ]
    MERIS_TRNG = [ 10-5, 10+5 ]
        
    