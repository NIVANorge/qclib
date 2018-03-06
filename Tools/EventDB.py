'''
Created on 18. apr. 2017

@author: PJA
'''
import datetime

from pyTools.ToolsManager import TOOLSMGR
from pyTools.ToolsManager import Declare

import simplekml

from . import Base
from .. import Globals
from ..Database import EventDB
from .. import Loggers

log = Loggers.getLogger(__name__)


class UnknowEventsKML(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(UnknowEventsKML, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            db   = EventDB.EventDB()
            kml  = simplekml.Kml()
            recs = db.fetch(EventDB.Schema.UnknownPosition)
            for r in recs:
                lon = Globals.SQLTransformations.sql2pos(r.lon)
                lat = Globals.SQLTransformations.sql2pos(r.lat)                
                kml.newpoint(name=str(r.id), coords=[(lon, lat)])
            kml.save(kw['kml_file'])
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('events.unknown.kml', execute, 'Generate KML file for unknown events')
    cmd.option('kml-file', 'Name for output KML file', default='unknown.kml')
    cmd.register(TOOLSMGR)

class AllEventsKML(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(AllEventsKML, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            db   = EventDB.EventDB()
            kml  = simplekml.Kml()
            sql = db.session.query(EventDB.Schema.Event)
            for r in sql:
                lon = Globals.SQLTransformations.sql2pos(r.longitude)
                lat = Globals.SQLTransformations.sql2pos(r.latitude)
                n = kml.newpoint(name=str(r.id), coords=[(lon, lat)])
                if r.type.code == Globals.EventTypes.IGNORED:
                    n.iconstyle.color = 'orange'
                elif r.type.code == Globals.EventTypes.UNKNOWN:
                    n.iconstyle.color = 'red'
                else:
                    n.iconstyle.color = 'green'
            kml.save(kw['kml_file'])
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('events.all.kml', execute, 'Generate KML file for all events')
    cmd.option('kml-file', 'Name for output KML file', default='events.kml')
    cmd.register(TOOLSMGR)


class UnknowEventsCleanup(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(UnknowEventsCleanup, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        sql2pos = Globals.SQLTransformations.sql2pos
        try:
            db     = EventDB.EventDB()
            bad_id = db.unknown_port().id
            recs   = db.fetch(EventDB.Schema.Event, id_port=bad_id)
            for r in recs:
                if not db.first(EventDB.Schema.UnknownPosition, id_event=r.id):
                    data = { 'lat': sql2pos(r.latitude), 'lon': sql2pos(r.longitude) }
                    db.register_unknown_position(r.id, **data)
                lon = Globals.SQLTransformations.sql2pos(r.longitude)
                lat = Globals.SQLTransformations.sql2pos(r.latitude)                
                port = db.find_port(lon, lat)
                if port.id != bad_id:
                    db.update_event(r.id, id_port=port.id)
                    rlst = db.fetch(EventDB.Schema.UnknownPosition, id_event=r.id)
                    for p in rlst:
                        db.delete(EventDB.Schema.UnknownPosition, id=p.id)   
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('events.unknown.cleanup', execute, 'Cleanup unknown ports (find a known port)')
    cmd.register(TOOLSMGR)
    
class RegisterPort(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(RegisterPort, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            sql2pos = Globals.SQLTransformations.sql2pos
            pos2sql = Globals.SQLTransformations.pos2sql
            db   = EventDB.EventDB()
            rec  = db.first(EventDB.Schema.UnknownPosition, id=kw['id'])
            rll  = [ sql2pos(rec.lon), sql2pos(rec.lat) ]
            port = db.first(EventDB.Schema.Port, code=kw['code'])
            if port:
                pll = [ 
                       [ sql2pos(port.lon_min), sql2pos(port.lon_max) ],
                       [ sql2pos(port.lat_min), sql2pos(port.lat_max) ],
                       ]
                lat_min = min([ pll[1][0], rll[1] ])
                lat_max = max([ pll[1][0], rll[1] ])
                lon_min = min([ pll[0][0], rll[0] ])
                lon_max = max([ pll[0][1], rll[0] ])
                new_val = { 
                           'lat_min': pos2sql(lat_min), 
                           'lat_max': pos2sql(lat_max), 
                           'lon_min': pos2sql(lon_min), 
                           'lon_max': pos2sql(lon_max)
                           }
                db.update(EventDB.Schema.Port, new_val, id=port.id)
            else:
                log.warning('Port not found, trying to register new entry')
                if ('name' not in kw) or (not kw['name']):
                    raise ValueError('Missing name for new port')
                new_val = { 
                           'lat_min': rec.lat, 'lat_max': rec.lat, 
                           'lon_min': rec.lon, 'lon_max': rec.lon }
                new_val['code'] = kw['code']
                new_val['name'] = kw['name']
                port = db.get_insert(EventDB.Schema.Port, **new_val)
            db.update_event(rec.id_event, id_port=port.id)
            db.delete(EventDB.Schema.UnknownPosition, id=rec.id)
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('port.register', execute, 'Register a port for an unknown position')
    cmd.option('id', 'database ID of unknown position', type=int)
    cmd.option('code', 'code of port')
    cmd.option('name', 'name of port')
    cmd.register(TOOLSMGR)

class ReRegisterPort(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(ReRegisterPort, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            sql2pos = Globals.SQLTransformations.sql2pos
            pos2sql = Globals.SQLTransformations.pos2sql
            db   = EventDB.EventDB()
            rec  = db.first(EventDB.Schema.Event, id=kw['id'])
            rll  = [ sql2pos(rec.longitude), sql2pos(rec.latitude) ]
            port = db.first(EventDB.Schema.Port, code=kw['code'])
            if port:
                pll = [ 
                       [ sql2pos(port.lon_min), sql2pos(port.lon_max) ],
                       [ sql2pos(port.lat_min), sql2pos(port.lat_max) ],
                       ]
                lat_min = min([ pll[1][0], rll[1] ])
                lat_max = max([ pll[1][0], rll[1] ])
                lon_min = min([ pll[0][0], rll[0] ])
                lon_max = max([ pll[0][1], rll[0] ])
                new_val = { 
                           'lat_min': pos2sql(lat_min), 
                           'lat_max': pos2sql(lat_max), 
                           'lon_min': pos2sql(lon_min), 
                           'lon_max': pos2sql(lon_max)
                           }
                db.update(EventDB.Schema.Port, new_val, id=port.id)
            else:
                log.warning('Port not found, trying to register new entry')
                if ('name' not in kw) or (not kw['name']):
                    raise ValueError('Missing name for new port')
                new_val = { 
                           'lat_min': rec.latitude, 'lat_max': rec.latitude, 
                           'lon_min': rec.longitude, 'lon_max': rec.longitude }
                new_val['code'] = kw['code']
                new_val['name'] = kw['name']
                port = db.get_insert(EventDB.Schema.Port, **new_val)
            db.update_event(rec.id, id_port=port.id)
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('port.reregister', execute, 'Reregister a port for an event position')
    cmd.option('id', 'database ID of event position', type=int)
    cmd.option('code', 'code of port')
    cmd.option('name', 'name of port')
    cmd.register(TOOLSMGR)

class IgnoreUnknownEvents(Base.BaseTool):
    
    @classmethod
    def execute(cls, *args, **kw):
        r = super(IgnoreUnknownEvents, cls).execute(*args, **kw)
        return(r)
      
    @classmethod
    def main(cls, *args, **kw):
        try:
            db     = EventDB.EventDB()
            bad_id = db.unknown_port().id
            ign_id = db.get_insert(EventDB.Schema.EventType, code=Globals.EventTypes.IGNORED)
            recs   = db.fetch(EventDB.Schema.UnknownPosition)
            for r in recs:
                values = { 'id_type':ign_id.id, 'update_time':datetime.datetime.now() }
                db.update(EventDB.Schema.Event, values, id=r.id_event)
                db.delete(EventDB.Schema.UnknownPosition, id=r.id)
            db.close()
        except Exception as err:
            raise(err)
        return

    cmd = Declare('events.unknown.ignore', execute, 'Register all unknown events to be ignoed')
    cmd.register(TOOLSMGR)
