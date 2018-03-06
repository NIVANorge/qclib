
import os
import datetime

import netCDF4
import numpy as np

from .. import Loggers
from .. import Globals
from ..netCDF import ncOperations
from ..netCDF import Generic

from . import Schema

log = Loggers.getLogger(__name__)


#
# Class Utility
#

class PoolDB(Schema.Database):
                             
    def register_raw_file(self, ncf, status_code):
        try:
            nc = netCDF4.Dataset(ncf, 'r')
            platform = self.get_insert(Schema.Platform, code=nc.platform)
            provider = self.get_insert(Schema.Provider, code=nc.provider)
            day      = datetime.datetime.strptime(nc.day, Globals.D_FORMAT_USR).date()
            nc.close()
            day      = self.get_insert(Schema.Day, day=day)
            filerec  = self.get_insert(Schema.PoolFile, 
                                       name=os.path.basename(ncf), 
                                       id_day=day.id, 
                                       id_platform=platform.id, 
                                       id_provider=provider.id)
            self.update_parameters(ncf, id_file = filerec.id)
            status = self.get_insert(Schema.StatusCode, code=status_code)
            self.get_insert(Schema.FileStatus, 
                            id_file=filerec.id, 
                            id_status=status.id)
            log.info('registered new raw file', file=ncf, status=status_code)
        except Exception as err:
            raise(err)
        return
    
    def update_parameters(self, ncf, id_file=None):
        if (id_file is None):
            rec = self.get_insert(Schema.PoolFile, name=os.path.basename(ncf))
            id_file = rec.id
        ncobj = Generic.netCDF(ncf)
        nc    = ncobj._nc
        for (grp, vlst) in ncOperations.listVariables(nc):
            glst = filter(lambda x: x.startswith('_'), grp.split('/'))
            if len(glst) > 0:
                continue
            g = ncobj.chdir(grp)
            for vn in vlst:
                v = g.variables[vn]
                n = '/'.join([g.path, vn])
                u = ''
                if 'unit' in v.ncattrs():
                    u = v.unit
                p = self.first(Schema.Parameter, name=n)
                if p:
                    if (not p.unit) and u:
                        self.update(Schema.Parameter, { 'unit': u }, id=p.id)
                    elif p.unit and (not u):
                        v.unit = p.unit
                        u = p.unit
                    assert u == p.unit, 'Unit mismatch for variable %s' % (vn)              
                try:
                    p = self.get_insert(Schema.Parameter, name=n, unit=u)
                    m = self.get_insert(Schema.ParameterMapping, id_file=id_file, id_parameter=p.id)
                except Exception as err:
                    log.error(err)
                    raise(err)
        ncobj.close()
        return
        
        
    
    def update_file_status(self, ncf, stcode):
        nc = netCDF4.Dataset(ncf, 'r')
        platform = self.get_insert(Schema.Platform, code=nc.platform)
        provider = self.get_insert(Schema.Provider, code=nc.provider)
        day      = datetime.datetime.strptime(nc.day, Globals.D_FORMAT_USR).date()
        day      = self.get_insert(Schema.Day, day=day)
        filerec  = self.get_insert(Schema.PoolFile,
                                   name=os.path.basename(ncf), 
                                   id_day=day.id,  
                                   id_platform=platform.id, 
                                   id_provider=provider.id)
        status   = self.get_insert(Schema.StatusCode, code=stcode)
        self.add(Schema.FileStatus, 
                        id_file=filerec.id, 
                        id_status=status.id)
        nc.close()
        log.info('updated file status', file=ncf, status=stcode)
        return

    def update_operation(self, opname):
        op = self.get_insert(Schema.OperationCode, code=opname)
        self.add(Schema.Operation, id_operation=op.id)
        log.info('updated operation', operation=opname)
        return

    def list(self, table, **kw):
        sql = self.session.query(table)
        for column,condition in kw.items():
            if isinstance(column, basestring):
                column = getattr(table, column)
            if not isinstance(condition, list):
                condition = [ condition ]
            for cnd in condition:
                if '%' in cnd:
                    sql = sql.filter(column.like(cnd))
                else:
                    sql = sql.filter(column == cnd)
        lst = sql.all()
        lst = filter(lambda x: x is not None, lst)
        return(lst)
         

    def todoList_v0(self, opname, *status, **kw):
        """
        todoList - Return a list of files to process
        
        Arguments:
          opname (str): the name of the operation to perform
          status (str): a list of file status to be achieved
          kw          : dictionary for options
          
        Options:
          exclude (str): list of file status that should not be achieved
          
        If the operation has already been performed, file status is looked up 
        after the operation has been achieved. If several file status are 
        provided, these are applied like an OR operation.
        
        If option *exclude* is provided and the file status has achieved one of 
        the listed status, the file is removed from the list returned. 
        """
        if 'exclude' not in kw:
            kw['exclude'] = []
        op_code  = self.first(Schema.OperationCode, code=opname)
        st_codes = []
        for s in status:
            st_codes += self.list(Schema.StatusCode, code=s)
        x_codes  = []
        for s in kw['exclude']:
            x_codes += self.list(Schema.StatusCode, code=s)
        if op_code is not None:
            last_run = self.last(Schema.Operation, id_operation=op_code.id)
        else:
            last_run = None
        lst = []
        for c in st_codes:
            if not last_run:
                lst += self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id_status == c.id).all()
            else:
                lst += self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id_status == c.id, Schema.FileStatus.time >= last_run.time).all()
        flst = []
        for r in lst:
            l = []
            for x in x_codes:
                l += self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id_status == x.id, Schema.FileStatus.id_file == r.id_file, Schema.FileStatus.time > r.time).all()
            if len(l):
                continue
            d = { 
                 'file'    : r.pool_file.name, 
                 'provider': r.pool_file.provider.code, 
                 'platform': r.pool_file.platform.code, 
                 'day'     : r.pool_file.day.day,
                 'year'    : r.pool_file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)

    def lastStatusQuery_v0(self, id_status, **kw):
        s0 = self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id_status == id_status)
        s0 = s0.subquery()
        s1 = self.session.query(Schema.sqa.func.max(s0.c.time).label('tmax')
                              ).group_by(s0.c.id_file).subquery()
        q = self.session.query(Schema.FileStatus).join(s1, 
                           Schema.sqa.and_(Schema.FileStatus.time)==s1.c.tmax
                           ).filter(Schema.FileStatus.id_status == id_status)
        for k in kw.keys():
            attr = getattr(Schema.FileStatus, k)
            q = q.filter(attr == kw[k])
        return(q)

    def lastStatusQuery_v1(self, id_status):
        fs_t = Schema.FileStatus.time
        fs_f = Schema.FileStatus.id_file
        fs_s = Schema.FileStatus.id_status
        tmax = Schema.sqa.func.max(fs_t).label('tmax')
        sql = self.session.query(tmax, fs_t, fs_s, fs_f)
        sql = sql.filter(fs_s == id_status)
        sql = sql.group_by(fs_f, fs_t)
        return(sql)


    def lastStatusQuery(self, id_status=None, **kw):
        fs_s = Schema.FileStatus.id_status
        s0 = self.session.query(Schema.FileStatus)
        if id_status is not None:
            s0 = s0.filter(fs_s == id_status)
        s0 = s0.subquery()
        fs_t = Schema.sqa.func.max(s0.c.time).label('tmax')
        fs_f = s0.c.id_file
        s1 = self.session.query(fs_t, fs_f).group_by(fs_f).subquery()
        c  = Schema.sqa.and_(s1.c.tmax == s0.c.time, s1.c.id_file == s0.c.id_file)
        s2 = self.session.query(s0).join(s1, c).subquery()
        return(s2)

    def todoListByOp(self, opname, prev_status):
        st_rec = self.first(Schema.StatusCode, code=prev_status)
        op_rec = self.first(Schema.OperationCode, code=opname)
        if not st_rec:
            return([])
        if op_rec is not None:
            last_run = self.last(Schema.Operation, id_operation=op_rec.id)
            rlst = self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id_status == st_rec.id, Schema.FileStatus.time > last_run.time).all()            
        else:
            rlst = self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id_status == st_rec.id).all()
        flst = []
        for r in rlst:
            d = { 
                 'file'    : r.pool_file.name, 
                 'provider': r.pool_file.provider.code, 
                 'platform': r.pool_file.platform.code, 
                 'day'     : r.pool_file.day.day,
                 'year'    : r.pool_file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)

    def todoList_v1(self, prev_status, next_status, **kw):
        st_prev = self.first(Schema.StatusCode, code=prev_status)
        st_next = self.first(Schema.StatusCode, code=next_status)
        rlst = []
        if not st_prev:
            return([])
        q_prev = self.lastStatusQuery(st_prev.id)
        for r_prev in q_prev:
            r_next = None
            if st_next:
                r_next = self.lastStatusQuery(st_next.id, id_file=r_prev.id_file).first()
            if (not r_next) or (r_prev.time > r_next.time):
                rlst.append(r_prev)
        flst = []
        for r in rlst:
            d = { 
                 'file'    : r.pool_file.name, 
                 'provider': r.pool_file.provider.code, 
                 'platform': r.pool_file.platform.code, 
                 'day'     : r.pool_file.day.day,
                 'year'    : r.pool_file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)
        
    def todoList(self, prev_status, next_status, **kw):
        st_prev = self.first(Schema.StatusCode, code=prev_status)
        st_next = self.first(Schema.StatusCode, code=next_status)
        slst = []
        if not st_prev:
            return([])
        q_prev = self.lastStatusQuery(st_prev.id)
        if st_next:
            q_next = self.lastStatusQuery(st_next.id)
            sql   = self.session.query(q_prev)
            sql   = sql.join(q_next, q_prev.c.id_file == q_next.c.id_file)
            sql   = sql.filter(q_prev.c.time > q_next.c.time)
            slst.append(sql.subquery())
            ilst  = self.session.query(q_next.c.id_file)
            sql   = self.session.query(q_prev)
            sql   = sql.filter(q_prev.c.id_file.notin_(ilst))
            slst.append(sql.subquery())
        else:
            slst.append(self.session.query(q_prev).subquery())
        rlst = []
        for s in slst:
            sid   = self.session.query(s.c.id)
            sql   = self.session.query(Schema.FileStatus).filter(Schema.FileStatus.id.in_(sid))
            rlst += sql.all()
        flst = []
        for r in rlst:
            d = { 
                 'file'    : r.pool_file.name, 
                 'provider': r.pool_file.provider.code, 
                 'platform': r.pool_file.platform.code, 
                 'day'     : r.pool_file.day.day,
                 'year'    : r.pool_file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)
        
    
    
    
        

        
