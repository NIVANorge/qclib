"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry._PoolDB
==============



(C) 4. feb. 2016 Pierre Jaccard
"""

import os
import re
import datetime

from pyTools.Database.SqlAlchemy import Interfaces

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqa

from .. import Loggers
from .. import ConfigManager

log = Loggers.getLogger(__name__)

DBCONF = ConfigManager.sysconf['database']['nivabase']

Base = declarative_base()

WHITE_REG = re.compile('\s+', flags=re.UNICODE)

#------------------------------------------------------------------------------- 
# SQLALCHEMY ORM Model
#------------------------------------------------------------------------------- 

class IndreOsloFjord(Base):
    __tablename__ = 'INDRE_OSLOFJORD'
    ID                     = sqa.Column(sqa.Integer, primary_key=True)
    TIME                   = sqa.Column(sqa.DateTime, nullable=False)
    LONGITUDE              = sqa.Column(sqa.Float, nullable=False)
    LATITUDE               = sqa.Column(sqa.Float, nullable=False)
    SYSTEM_FLAG            = sqa.Column(sqa.Integer, default=0)
    TEMPERATURE            = sqa.Column(sqa.Float, nullable=False)
    TEMPERATURE_FLAG       = sqa.Column(sqa.Integer, default=0)
    SALINITY               = sqa.Column(sqa.Float, nullable=False)
    SALINITY_FLAG          = sqa.Column(sqa.Integer, default=0)
    CHLA_FLUORESCENCE      = sqa.Column(sqa.Float, nullable=False)
    CHLA_FLUORESCENCE_FLAG = sqa.Column(sqa.Integer, default=0)
    CDOM_FLUORESCENCE      = sqa.Column(sqa.Float, nullable=False)
    CDOM_FLUORESCENCE_FLAG = sqa.Column(sqa.Integer, default=0)
    TURBIDITY              = sqa.Column(sqa.Float, nullable=False)
    TURBIDITY_FLAG         = sqa.Column(sqa.Integer, default=0)

#
# Class Utility
#

class Database(Interfaces.OracleInterface):
    
    def __init__(self):
        super(Database, self).__init__(DBCONF, Base)
        return
        
    
    def insert_record(self, drec):
        try:
            o = self.first(IndreOsloFjord, TIME=drec['TIME'])
            if o is None:
                o = self.add(IndreOsloFjord, **drec)
            else:
                self.update(IndreOsloFjord, drec, ID=o.ID)
        except Exception as err:
            log.error(err)
            raise(err)
        return(o.ID)
    
        
        

        
