'''
Created on 3. apr. 2017

@author: PJA
'''

import cx_Oracle

from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare


from . import Base
from .. import ConfigManager


DBCONF = ConfigManager.sysconf['database']['nivabase']


class UpdateFERRYBOX(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(UpdateFERRYBOX, cls).execute(*args, **kw)
        return(r)
    
    @classmethod
    def main(cls, *args, **kw):
        try:
            dsn = cx_Oracle.makedsn(DBCONF['host'], DBCONF['port'], DBCONF['sid'])
            cxn = cx_Oracle.connect(DBCONF['user'], DBCONF['pass'], dsn)
            crs = cx_Oracle.Cursor(cxn)
            crs.callproc("ferrybox.pkg_aquamonitor.update_product", ['INDRE_OSLOFJORD'])
            cxn.commit()
            crs.close()
            cxn.close()
        except Exception as err:
            raise(err)
        return
    
    cmd = Declare('nivabase.update', execute, 'Update content of NIVABASE')
    cmd.register(TOOLSMGR)
