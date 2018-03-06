"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Tools.Pool
===========================



(C) 10. okt. 2016 Pierre Jaccard
"""

from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare

from . import Base

from .. import Loggers

from pyFerry.Operations import Export as Export_ops

log = Loggers.getLogger(__name__)

class SSRDVExport(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(SSRDVExport, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = Export_ops.ExportSSRDV.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.export.ssrdv', execute, 'Launch processor for exporting data to SSRDV')
    cmd.register(TOOLSMGR)

class IndreOsloFjordExport(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(IndreOsloFjordExport, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = Export_ops.ExportIndreOsloFjord.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.export.iof', execute, 'Launch processor for exporting data to IOF')
    cmd.register(TOOLSMGR)

class JERICOExport(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(JERICOExport, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = Export_ops.ExportJERICO.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.export.jerico', execute, 'Launch processor for exporting data for JERICO')
    cmd.register(TOOLSMGR)

class CMEMSExport(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(CMEMSExport, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = Export_ops.ExportCMEMS.execute()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('processor.export.cmems', execute, 'Launch processor for exporting data to CMEMS')
    cmd.register(TOOLSMGR)
