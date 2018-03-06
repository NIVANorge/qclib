

from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare

from . import Base

from .. import Loggers
from ..Operations.Incoming import Incoming
from ..Operations.BaseOperations import BaseOperation

log = Loggers.getLogger(__name__)

class IncomingTool(Base.BaseTool):
  
    @classmethod
    def execute(cls, *args, **kw):
        r = super(IncomingTool, cls).execute(*args, **kw)
        return(r)
      
    def main(self, *args, **kw):
        o  = Incoming()
        BaseOperation.execute('incoming', o.pending)
        return
    
    cmd = Declare('processor.incoming', execute, 'Launch incoming processor')
    cmd.register(TOOLSMGR)
