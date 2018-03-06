

from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare


from . import Base

from .. import Loggers
from ..Operations import Import

log = Loggers.getLogger(__name__)

class ImportLog(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(ImportLog, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            o = Import.Importer.execute()
        except Exception as err:
            raise(err)
        return


    cmd = Declare('processor.importlog', execute, 'Launch import processor')
    cmd.register(TOOLSMGR)
