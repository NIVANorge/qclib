"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.PoolDB
==============



(C) 4. feb. 2016 Pierre Jaccard
"""

import os
import datetime

import netCDF4
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqa
import sqlalchemy.orm as orm

from . import Loggers
from . import ConfigManager
from . import Globals

log = Loggers.getLogger(__name__)

DBFILE = ConfigManager.abspath(ConfigManager.sysconf['pool']['database'])

Base = declarative_base()

#------------------------------------------------------------------------------- 
# SQLALCHEMY ORM Model
#------------------------------------------------------------------------------- 


class Platform(Base):
    __tablename__ = 'platforms'
    id    = sqa.Column(sqa.Integer, primary_key=True)
    code  = sqa.Column(sqa.String, unique=True)

class Provider(Base):
    __tablename__ = 'providers'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String, unique=True)

class Day(Base):
    __tablename__ = 'days'
    id  = sqa.Column(sqa.Integer, primary_key=True)
    day = sqa.Column(sqa.Date, unique=True)
    
class Parameter(Base):
    __tablename__ = 'parameters'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    name = sqa.Column(sqa.String, unique=True)
    unit = sqa.Column(sqa.String, unique=False)
    
class File(Base):
    __tablename__ = 'files'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    id_platform = sqa.Column(sqa.Integer, sqa.ForeignKey('platforms.id'))
    id_provider = sqa.Column(sqa.Integer, sqa.ForeignKey('providers.id'))
    id_day      = sqa.Column(sqa.Integer, sqa.ForeignKey('days.id'))
    name        = sqa.Column(sqa.String, unique=True)
    platform    = orm.relationship("Platform" , backref=orm.backref('files', order_by=id))
    provider    = orm.relationship("Provider", backref=orm.backref('files', order_by=id))
    day         = orm.relationship("Day", backref=orm.backref('files', order_by=id))

class StatusCode(Base):
    __tablename__ = 'status_codes'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String, unique=True)

class FileStatus(Base):
    __tablename__ = 'files_status'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    time        = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    id_file     = sqa.Column(sqa.Integer, sqa.ForeignKey('files.id'))
    id_status   = sqa.Column(sqa.Integer, sqa.ForeignKey('status_codes.id'))
    file        = orm.relationship("File" , backref=orm.backref('files_status', order_by=id))
    status      = orm.relationship("StatusCode", backref=orm.backref('files_status', order_by=id))

class OperationCode(Base):
    __tablename__ = 'operation_codes'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String, unique=True)

class Operation(Base):
    __tablename__ = 'operations'    
    id            = sqa.Column(sqa.Integer, primary_key=True)
    time          = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    id_operation  = sqa.Column(sqa.Integer, sqa.ForeignKey('operation_codes.id'))
    operation     = orm.relationship("OperationCode", backref=orm.backref('operations', order_by=id))

class ParameterMapping(Base):
    __tablename__ = 'parameter_mappings'
    id           = sqa.Column(sqa.Integer, primary_key=True)
    id_file      = sqa.Column(sqa.Integer, sqa.ForeignKey('files.id'))
    id_parameter = sqa.Column(sqa.Integer, sqa.ForeignKey('parameters.id'))
    file         = orm.relationship("File" , backref=orm.backref('installation_mappings', order_by=id))
    parameter    = orm.relationship("Parameter" , backref=orm.backref('installation_mappings', order_by=id))

#
# Class Utility
#

class PoolDB(object):
    
    def __init__(self):
        self.dbfile = DBFILE
        self.session = None
        self.session_class = None
        self.engine = sqa.create_engine('sqlite:///' + self.dbfile, echo=False)
        Base.metadata.create_all(self.engine)
        self.session_class = orm.sessionmaker(bind=self.engine)
        self.session = self.session_class()
        return

    def close(self):
        self._close_(self)
        return
        
    @classmethod
    def _close_(cls, obj):
        obj.flush()
        if obj.session is not None:
            obj.session.close()
            obj.session = None
        return

    def __del__(self):
        self._close_(self)
        return

    def commit(self):
        if self.session is not None:
            self.session.commit()
        return

    def flush(self):
        self.commit()
        if self.session is not None:
            self.session.flush()
        return

    def has(self, table, **kw):
        o = self.first(table, **kw)
        return(o is not None)

    def add(self, table, **kw):
        o = table()
        map(lambda x: setattr(o, x, kw[x]), kw.keys())
        self.session.add(o)
        self.flush()
        return(o)

    def first(self, table, **kw):
        o = self.session.query(table).filter_by(**kw).first()
        return(o)

    def last(self, table, **kw):
        id_attr = getattr(table, 'id')
        o = self.session.query(table).filter_by(**kw).order_by(id_attr.desc()).first()
        return(o)

    def get_insert(self, table, **kw):
        o = self.first(table, **kw)
        if o is None:
            o = self.add(table, **kw)
        return(o)

    def update(self, table, values, **kw):
        self.session.query(table).filter_by(**kw).update(values)
        return

    def fetch(self, table, **kw):
        o = self.session.query(table).filter_by(**kw).all()
        return(o)
                         
    def register_raw_file(self, ncf, status_code):
        try:
            nc = netCDF4.Dataset(ncf, 'r')
            platform = self.get_insert(Platform, code=nc.platform)
            provider = self.get_insert(Provider, code=nc.provider)
            day      = datetime.datetime.strptime(nc.day, Globals.D_FORMAT_USR).date()
            day      = self.get_insert(Day, day=day)
            filerec  = self.get_insert(File, 
                                       name=os.path.basename(ncf), 
                                       id_day=day.id, 
                                       id_platform=platform.id, 
                                       id_provider=provider.id)
            raw = nc.groups['raw']
            for ncg in raw.groups.values():
                for vn,ncv in ncg.variables.items():
                    grp  = ncv.group()
                    name = filter(lambda x: len(x) > 0, grp.path.split('/'))
                    name = '_'.join(name + [vn])
                    parameter = self.get_insert(Parameter, name=name, unit=ncv.unit)
                    self.get_insert(ParameterMapping, 
                                   id_file=filerec.id, 
                                   id_parameter=parameter.id,
                                   )
            status = self.get_insert(StatusCode, code=status_code)
            self.get_insert(FileStatus, 
                            id_file=filerec.id, 
                            id_status=status.id)
            log.info('registered new raw file', file=ncf, status=status_code)
        except Exception as err:
            raise(err)
        return
    
    def update_file_status(self, ncf, stcode):
        nc = netCDF4.Dataset(ncf, 'r')
        platform = self.get_insert(Platform, code=nc.platform)
        provider = self.get_insert(Provider, code=nc.provider)
        day      = datetime.datetime.strptime(nc.day, Globals.D_FORMAT_USR).date()
        day      = self.get_insert(Day, day=day)
        filerec  = self.get_insert(File,
                                   name=os.path.basename(ncf), 
                                   id_day=day.id,  
                                   id_platform=platform.id, 
                                   id_provider=provider.id)
        status   = self.get_insert(StatusCode, code=stcode)
        self.add(FileStatus, 
                        id_file=filerec.id, 
                        id_status=status.id)
        nc.close()
        log.info('updated file status', file=ncf, status=stcode)
        return

    def update_operation(self, opname):
        op = self.get_insert(OperationCode, code=opname)
        self.add(Operation, id_operation=op.id)
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
        op_code  = self.first(OperationCode, code=opname)
        st_codes = []
        for s in status:
            st_codes += self.list(StatusCode, code=s)
        x_codes  = []
        for s in kw['exclude']:
            x_codes += self.list(StatusCode, code=s)
        if op_code is not None:
            last_run = self.last(Operation, id_operation=op_code.id)
        else:
            last_run = None
        lst = []
        for c in st_codes:
            if not last_run:
                lst += self.session.query(FileStatus).filter(FileStatus.id_status == c.id).all()
            else:
                lst += self.session.query(FileStatus).filter(FileStatus.id_status == c.id, FileStatus.time >= last_run.time).all()
        flst = []
        for r in lst:
            l = []
            for x in x_codes:
                l += self.session.query(FileStatus).filter(FileStatus.id_status == x.id, FileStatus.id_file == r.id_file, FileStatus.time > r.time).all()
            if len(l):
                continue
            d = { 
                 'file'    : r.file.name, 
                 'provider': r.file.provider.code, 
                 'platform': r.file.platform.code, 
                 'day'     : r.file.day.day,
                 'year'    : r.file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)

    def lastStatusQuery(self, id_status, **kw):
        s0 = self.session.query(FileStatus).filter(FileStatus.id_status == id_status)
        s0 = s0.subquery()
        s1 = self.session.query(sqa.func.max(s0.c.time).label('tmax')
                              ).group_by(s0.c.id_file).subquery()
        q = self.session.query(FileStatus).join(s1, 
                           sqa.and_(FileStatus.time)==s1.c.tmax
                           ).filter(FileStatus.id_status == id_status)
        for k in kw.keys():
            attr = getattr(FileStatus, k)
            q = q.filter(attr == kw[k])
        return(q)

    def todoListByOp(self, opname, prev_status):
        st_rec = self.first(StatusCode, code=prev_status)
        op_rec = self.first(OperationCode, code=opname)
        if not st_rec:
            return([])
        if op_rec is not None:
            last_run = self.last(Operation, id_operation=op_rec.id)
            rlst = self.session.query(FileStatus).filter(FileStatus.id_status == st_rec.id, FileStatus.time > last_run.time).all()            
        else:
            rlst = self.session.query(FileStatus).filter(FileStatus.id_status == st_rec.id).all()
        flst = []
        for r in rlst:
            d = { 
                 'file'    : r.file.name, 
                 'provider': r.file.provider.code, 
                 'platform': r.file.platform.code, 
                 'day'     : r.file.day.day,
                 'year'    : r.file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)

        
    def todoList(self, prev_status, next_status, **kw):
        st_prev = self.first(StatusCode, code=prev_status)
        st_next = self.first(StatusCode, code=next_status)
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
                 'file'    : r.file.name, 
                 'provider': r.file.provider.code, 
                 'platform': r.file.platform.code, 
                 'day'     : r.file.day.day,
                 'year'    : r.file.day.day.strftime('%Y'),
                 'status'  : r.status.code
                 }
            flst.append(d)
        return(flst)
        
    
    
    
        

        
