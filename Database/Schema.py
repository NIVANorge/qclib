'''
Created on 31. okt. 2017

@author: PJA
'''

import datetime

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqa
import sqlalchemy.orm as orm

from pyTools.Database.SqlAlchemy import Interfaces

from .. import ConfigManager

Base = declarative_base()

DBCONF = ConfigManager.sysconf['database']['system']

class Platform(Base):
    __tablename__ = 'platforms'
    id    = sqa.Column(sqa.Integer, primary_key=True)
    code  = sqa.Column(sqa.String(16), unique=True)
    name  = sqa.Column(sqa.String(64), unique=False)
    ices  = sqa.Column(sqa.String(16), unique=True)
    imo   = sqa.Column(sqa.String(16), unique=False)
    sign  = sqa.Column(sqa.String(16), unique=False)


class Provider(Base):
    __tablename__ = 'providers'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String(16), unique=True)

class Port(Base):
    __tablename__ = 'ports'    
    id            = sqa.Column(sqa.Integer, primary_key=True)
    lat_min       = sqa.Column(sqa.Float)
    lat_max       = sqa.Column(sqa.Float)
    lon_min       = sqa.Column(sqa.Float)
    lon_max       = sqa.Column(sqa.Float)
    name          = sqa.Column(sqa.String(64), unique=False, default='UNKNOWN')
    code          = sqa.Column(sqa.String(16), unique=False, default='?')

class EventType(Base):
    __tablename__ = 'event_types'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    code        = sqa.Column(sqa.String(32), unique=True)

class Event(Base):
    __tablename__ = 'events'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    latitude    = sqa.Column(sqa.Float)
    longitude   = sqa.Column(sqa.Float)
    id_platform = sqa.Column(sqa.Integer, sqa.ForeignKey('platforms.id'))
    id_provider = sqa.Column(sqa.Integer, sqa.ForeignKey('providers.id'))
    id_port     = sqa.Column(sqa.Integer, sqa.ForeignKey('ports.id')) 
    id_type     = sqa.Column(sqa.Integer, sqa.ForeignKey('event_types.id')) 
    event_time  = sqa.Column(sqa.DateTime)
    update_time = sqa.Column(sqa.DateTime, default=datetime.datetime.now())
    platform    = orm.relationship("Platform" , backref=orm.backref('events', order_by=id))
    provider    = orm.relationship("Provider", backref=orm.backref('events', order_by=id))
    port        = orm.relationship("Port", backref=orm.backref('events', order_by=id))
    type        = orm.relationship("EventType", backref=orm.backref('events', order_by=id))

class UnknownPosition(Base):
    __tablename__ = 'unknown_positions'    
    id            = sqa.Column(sqa.Integer, primary_key=True)
    lat           = sqa.Column(sqa.Float)
    lon           = sqa.Column(sqa.Float)
    id_event      = sqa.Column(sqa.Integer, sqa.ForeignKey('events.id'))
    event         = orm.relationship("Event", backref=orm.backref('events', order_by=id))


class PortCall(Base):
    __tablename__ = 'port_calls'    
    id           = sqa.Column(sqa.Integer, primary_key=True)
    id_arrival   = sqa.Column(sqa.Integer, sqa.ForeignKey('events.id'))
    id_departure = sqa.Column(sqa.Integer, sqa.ForeignKey('events.id'))
    update_time  = sqa.Column(sqa.DateTime, default=datetime.datetime.now())    
    departure    = orm.relationship("Event" , foreign_keys=[id_departure])
    arrival      = orm.relationship("Event" , foreign_keys=[id_arrival])
    
class Transect(Base):
    __tablename__ = 'transects'    
    id           = sqa.Column(sqa.Integer, primary_key=True)
    id_departure = sqa.Column(sqa.Integer, sqa.ForeignKey('events.id'))
    id_arrival   = sqa.Column(sqa.Integer, sqa.ForeignKey('events.id'))
    transect_id  = sqa.Column(sqa.String(128), unique=True)
    update_time  = sqa.Column(sqa.DateTime, default=datetime.datetime.now())    
    departure    = orm.relationship("Event" , foreign_keys=[id_departure])
    arrival      = orm.relationship("Event" , foreign_keys=[id_arrival])

class Route(Base):
    __tablename__ = 'routes'    
    id           = sqa.Column(sqa.Integer, primary_key=True)
    id_platform  = sqa.Column(sqa.Integer, sqa.ForeignKey('platforms.id'))
    id_start     = sqa.Column(sqa.Integer, sqa.ForeignKey('ports.id'))
    id_stop      = sqa.Column(sqa.Integer, sqa.ForeignKey('ports.id'))
    update_time  = sqa.Column(sqa.DateTime, default=datetime.datetime.now())    
    platform     = orm.relationship("Platform" , foreign_keys=[id_platform])
    start        = orm.relationship("Port" , foreign_keys=[id_start])
    stop         = orm.relationship("Port" , foreign_keys=[id_stop])

class RawFile(Base):
    __tablename__ = 'raw_files'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    id_platform = sqa.Column(sqa.Integer, sqa.ForeignKey('platforms.id'))
    id_provider = sqa.Column(sqa.Integer, sqa.ForeignKey('providers.id'))
    time        = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    name        = sqa.Column(sqa.String(64), unique=False)
    md5         = sqa.Column(sqa.String(64), unique=True)
    platform    = orm.relationship("Platform" , backref=orm.backref('raw_files', order_by=id))
    provider    = orm.relationship("Provider", backref=orm.backref('raw_files', order_by=id))

class Import(Base):
    __tablename__ = 'imports'    
    id            = sqa.Column(sqa.Integer, primary_key=True)
    time          = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    id_file       = sqa.Column(sqa.Integer, sqa.ForeignKey('raw_files.id'))
    raw_file      = orm.relationship("RawFile", backref=orm.backref('raw_files', order_by=id))

class Day(Base):
    __tablename__ = 'days'
    id  = sqa.Column(sqa.Integer, primary_key=True)
    day = sqa.Column(sqa.Date, unique=True)
    
class Parameter(Base):
    __tablename__ = 'parameters'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    name = sqa.Column(sqa.String(64), unique=True)
    unit = sqa.Column(sqa.String(64), unique=False)
    
class PoolFile(Base):
    __tablename__ = 'pool_files'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    id_platform = sqa.Column(sqa.Integer, sqa.ForeignKey('platforms.id'))
    id_provider = sqa.Column(sqa.Integer, sqa.ForeignKey('providers.id'))
    id_day      = sqa.Column(sqa.Integer, sqa.ForeignKey('days.id'))
    name        = sqa.Column(sqa.String(32), unique=True)
    platform    = orm.relationship("Platform" , backref=orm.backref('pool_files', order_by=id))
    provider    = orm.relationship("Provider", backref=orm.backref('pool_files', order_by=id))
    day         = orm.relationship("Day", backref=orm.backref('pool_files', order_by=id))

class StatusCode(Base):
    __tablename__ = 'status_codes'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String(32), unique=True)

class FileStatus(Base):
    __tablename__ = 'files_status'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    time        = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    id_file     = sqa.Column(sqa.Integer, sqa.ForeignKey('pool_files.id'))
    id_status   = sqa.Column(sqa.Integer, sqa.ForeignKey('status_codes.id'))
    pool_file   = orm.relationship("PoolFile" , backref=orm.backref('files_status', order_by=id))
    status      = orm.relationship("StatusCode", backref=orm.backref('files_status', order_by=id))

class OperationCode(Base):
    __tablename__ = 'operation_codes'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String(32), unique=True)

class Operation(Base):
    __tablename__ = 'operations'    
    id            = sqa.Column(sqa.Integer, primary_key=True)
    time          = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    id_operation  = sqa.Column(sqa.Integer, sqa.ForeignKey('operation_codes.id'))
    operation     = orm.relationship("OperationCode", backref=orm.backref('operations', order_by=id))

class ParameterMapping(Base):
    __tablename__ = 'parameter_mappings'
    id           = sqa.Column(sqa.Integer, primary_key=True)
    id_file      = sqa.Column(sqa.Integer, sqa.ForeignKey('pool_files.id'))
    id_parameter = sqa.Column(sqa.Integer, sqa.ForeignKey('parameters.id'))
    pool_file    = orm.relationship("PoolFile" , backref=orm.backref('parameter_mappings', order_by=id))
    parameter    = orm.relationship("Parameter" , backref=orm.backref('parameter_mappings', order_by=id))

class Database(Interfaces.MySQLInterface):
    
    def __init__(self):
        super(Database, self).__init__(DBCONF, Base)
        return
