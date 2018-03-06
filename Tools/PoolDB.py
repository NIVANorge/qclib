"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Tools.Pool
===========================



(C) 10. okt. 2016 Pierre Jaccard
"""

import os

import netCDF4
from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare

from ..netCDF import Generic


from .. import Loggers
from .. import FolderManagers
from ..Database import PoolDB
from ..Database import Schema

from . import Base

log = Loggers.getLogger(__name__)


class CleanTables(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(CleanTables, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def cleanPoolFile(cls):
        try:
            root = FolderManagers.PoolRoot()
            db   = PoolDB.PoolDB()
            for rec in db.fetch(Schema.PoolFile):
                cdict = Generic.netCDF.ncDict(rec.name)
                clst  = root.cnames_from_dict(cdict)
                if not root.inPool(rec.name, *clst):
                    db.delete(Schema.FileStatus, id_file=rec.id)
                    db.delete(Schema.ParameterMapping, id_file=rec.id)
                    db.delete(Schema.PoolFile, id=rec.id)
            db.close()
        except Exception as err:
            raise(err)
        return
            
    @classmethod
    def main(cls, *args, **kw):
        try:
            cls.cleanPoolFile()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('pooldb.clean', execute, 'Cleans tables in PoolDB')
    cmd.register(TOOLSMGR)


class RebuildParameterTables(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(RebuildParameterTables, cls).execute(*args, **kw)
        return(r)
         
    @classmethod
    def main(cls, *args, **kw):
        try:
            root = FolderManagers.PoolRoot()
            db   = PoolDB.PoolDB()
            flst = root.files(matchf='*.nc')
            for f in flst:
                b   = os.path.basename(f)
                nc = netCDF4.Dataset(f, mode='r')
                db.update_parameters(nc)
                nc.close()
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('pooldb.parameters.rebuild', execute, 'Rebuild the parameters related tables')
    cmd.register(TOOLSMGR)

