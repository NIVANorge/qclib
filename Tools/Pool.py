"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Tools.Pool
===========================



(C) 10. okt. 2016 Pierre Jaccard
"""

from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare
from pyTools.Import import getObject

from . import Base

from .. import Loggers
from .. import Globals
from .. import FolderManagers
from pyFerry.Database import PoolDB

from pyFerry.Operations import RawGroup

log = Loggers.getLogger(__name__)

class RawDataCombiner(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(RawDataCombiner, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = RawGroup.RawCombiner.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.raw.combine', execute, 'Launch processor for merging raw data')
    cmd.register(TOOLSMGR)

class UpdateNavigation(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(UpdateNavigation, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = RawGroup.UpdateNavigation.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.raw.updatenav', execute, 'Launch processor for updating navigation data')
    cmd.register(TOOLSMGR)

class ApplyRTQC(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(ApplyRTQC, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = RawGroup.RTQC.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.raw.rtqc', execute, 'Launch processor for RTQC on raw data')
    cmd.register(TOOLSMGR)

class ScanForPortEvents(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(ScanForPortEvents, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = RawGroup.ScanForPortEvents.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.raw.events', execute, 'Scan for port events')
    cmd.register(TOOLSMGR)

class ScanForTransects(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(ScanForTransects, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = RawGroup.ScanForTransects.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.raw.transects', execute, 'Scan for new transects')
    cmd.register(TOOLSMGR)


class SortRawFerryboxTime(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(SortRawFerryboxTime, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            if '--' in kw:
                flst = kw['--']
                for f in flst:
                    pool = FolderManagers.PoolRoot()
                    pool.sortFile(f,'time', Globals.netCDFGroups.RAW_FERRYBOX)
        except Exception as err:
            raise(err)
        return

    cmd = Declare('raw.ferrybox.sort', execute, 'Sort raw ferrybox data by time (for specified files)')
    cmd.register(TOOLSMGR)

class SetFileStatus(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(SetFileStatus, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            if '--' in kw:
                st_name = 'pyFerry.Globals.FileStatus.' + args[0]
                st_code = getObject(st_name) 
                flst = kw['--']
                for f in flst:                    
                    db  = PoolDB.PoolDB()
                    db.update_file_status(f, st_code)
                    db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('pool.status.set', execute, 'Set new status for specified files')
    cmd.argument('status', 'New status (as in Globals)')
    cmd.register(TOOLSMGR)
