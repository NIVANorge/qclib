
import datetime

import numpy as np

from pyTools.Navigation import ll2m

from .. import Globals
from .. import Loggers
from . import Schema

log = Loggers.getLogger(__name__)


class UpdateRow(object):
    
    def __init__(self, table):
        self.table = table
        return
    
    def __call__(self, method):
        def wrapped(obj, entry_id, **values):
            if 'update_time' not in values:
                values['update_time'] = datetime.datetime.now()
            obj.update(self.table, values, id=entry_id)
            return    
        return(wrapped)

class NewEntriesSince(object):
    
    def __init__(self, table):
        self.table = table
        return
    
    def __call__(self, method):
        def wrapped(obj, t, **kw):
            attr = getattr(self.table, 'update_time')
            olst = obj.session.query(self.table).filter(attr >= t)
            if kw:
                olst = olst.filter_by(**kw)
            olst = olst.order_by(attr.asc())
            olst = olst.all()
            return(olst)
        return(wrapped)

    
class EventDB(Schema.Database):
    

    def register_platform(self, code):
        r = self.get_insert(Schema.Platform, code=code)
        return(r.id)

    def register_provider(self, code):
        r = self.get_insert(Schema.Provider, code=code)
        return(r.id)

    def register_event_type(self, code):
        r = self.get_insert(Schema.EventType, code=code)
        return(r.id)
 
    def unknown_port(self):
        r = self.get_insert(Schema.Port, lat_min=0, lat_max=0, lon_min=0, lon_max=0, name='UNKNOWN', code='NA')
        return(r)

    def ignored_port(self):
        r = self.get_insert(Schema.Port, lat_min=0, lat_max=0, lon_min=0, lon_max=0, name='UNKNOWN', code='NA')
        return(r)
        
    def register_unknown_position(self, id_event, **kw):
        data = {}
        for k in ('lat', 'latitude', 'lon', 'longitude'):
            if k in kw:
                data[k] = kw[k]
        if 'latitude' in kw:
            data['lat'] = data['latitude']
        if 'longitude' in kw:
            data['lon'] = data['longitude']
        kw['lon'] = Globals.SQLTransformations.pos2sql(kw['lon'])
        kw['lat'] = Globals.SQLTransformations.pos2sql(kw['lat'])
        r = self.get_insert(Schema.UnknownPosition, id_event=id_event, **kw)
        return(r.id)
            
    def find_port(self, lon, lat, **kw):
        ilon = Globals.SQLTransformations.pos2sql(lon)
        ilat = Globals.SQLTransformations.pos2sql(lat)
        if kw:
            olst = self.fetch(Schema.Port, **kw)
        else:
            olst = self.session.query(Schema.Port).filter(Schema.Port.lon_min <= ilon, Schema.Port.lon_max >= ilon, \
                                                Schema.Port.lat_min <= ilat, Schema.Port.lat_max >= ilat).all()
            if not len(olst):
                olst = [ self.closest_port(lon, lat) ]
        if len(olst) > 1:
            raise ValueError('too many port matching position')
        if not len(olst):
            olst = [ self.unknown_port() ]
        return(olst[0])                                        
    
    def closest_port(self, lon, lat):
        sql2pos = Globals.SQLTransformations.sql2pos
        recs = self.fetch(Schema.Port)
        port = None
        ds   = []
        ids  = []
        for i in range(len(recs)):
            r = recs[i]
            rlon = [ sql2pos(r.lon_min), sql2pos(r.lon_max) ]
            rlat = [ sql2pos(r.lat_min), sql2pos(r.lat_max) ]
            x = np.array([ lon, 0.5*(rlon[0] + rlon[1]) ])
            y = np.array([ lat, 0.5*(rlat[0] + rlat[1]) ])
            ds.append(ll2m(x, y)[0])
            ids.append(r.id)
        if len(ds) > 0:
            idx  = np.argsort(ds)
            imin = idx[0]
            if ds[imin] < 1852.0:
                port = self.find_port(0, 0, id=ids[imin])
        if port is None:
            port = self.unknown_port()
        return(port)
    
    def register_event(self, time, **kw):
        kw['longitude'] = Globals.SQLTransformations.pos2sql(kw['longitude'])
        kw['latitude']  = Globals.SQLTransformations.pos2sql(kw['latitude'])
        r = self.get_insert(Schema.Event, event_time=time, **kw)
        return(r.id)
    
    def register_arrival(self, time, **kw):
        kw['id_type'] = self.get_insert(Schema.EventType, code=Globals.EventTypes.ARRIVAL)
        self.register_event(time, **kw)
        return

    def register_departure(self, time, **kw):
        kw['id_type'] = self.get_insert(Schema.EventType, code=Globals.EventTypes.DEPARTURE)
        self.register_event(time, **kw)
        return
        
    def register_transect(self, rdep, rarr):
        s = [ rdep.provider.code, rdep.platform.code ]
        s.append(rdep.port.code)
        s.append(datetime.datetime.strftime(rdep.event_time, Globals.DT_FORMAT_ISO))
        s.append(rarr.port.code)
        s.append(datetime.datetime.strftime(rarr.event_time, Globals.DT_FORMAT_ISO))
        s = '_'.join(s)
        o = self.get_insert(Schema.Transect, id_departure=rdep.id, id_arrival=rarr.id, transect_id=s)
        return(o)
            
    @UpdateRow(Schema.Event)    
    def update_event(self, eid, **values): pass
  
    @NewEntriesSince(Schema.Event)        
    def new_events(self, t, **kw): pass
    
    def new_arrivals(self, t):
        idt  = self.first(Schema.EventType, code=Globals.EventTypes.ARRIVAL)
        olst = self.new_events(t, id_type=idt)
        return(olst)
    
    def new_departures(self, t):
        idt  = self.first(Schema.EventType, code=Globals.EventTypes.DEPARTURE)
        olst = self.new_events(t, id_type=idt.id)
        return(olst)
    
    def next_event(self, t, **kw):
        olst = self.session.query(Schema.Event).filter(Schema.Event.event_time > t)
        if kw:
            olst = olst.filter_by(**kw)
        olst = olst.order_by(Schema.Event.event_time.asc()).first()
        return(olst)
        
    @NewEntriesSince(Schema.Transect)
    def new_transects(self, t, **kw): pass
    
    def find_route(self, transect):
        ship_id   = transect.departure.id_platform
        route_lst = self.fetch(Schema.Route, id_platform=ship_id)
        #
        start_t   = transect.departure.event_time
        start_ids = map(lambda x: x.id_start, route_lst)
        query = self.session.query(Schema.Transect).join(Schema.Transect.departure)
        query = query.join(Schema.Event.port)
        query = query.filter(Schema.Event.event_time <= start_t)
        query = query.filter(Schema.Event.id_platform == ship_id)
        query = query.filter(Schema.Event.id_port.in_(start_ids))
        query = query.order_by(Schema.Event.event_time.desc())
#         query = self.session.query(Transect).filter(  \
#             Transect.departure.event_time <= start_t, \
#             Transect.departure.id_platform == ship_id,\
#             Transect.departure.port.id.in_(start_ids)).order_by(Transect.departure.event_time.desc())
        start = query.first()
        #
        stop_t   = transect.arrival.event_time
        stop_ids = map(lambda x: x.id_stop, route_lst)
        query = self.session.query(Schema.Transect).join(Schema.Transect.arrival)
        query = query.join(Schema.Event.port)
        query = query.filter(Schema.Event.event_time >= stop_t)
        query = query.filter(Schema.Event.id_platform == ship_id)
        query = query.filter(Schema.Event.id_port.in_(stop_ids))
        query = query.order_by(Schema.Event.event_time.asc())
 #         query = self.session.query(Transect).filter(  \
#             Transect.arrival.event_time >= stop_t, \
#             Transect.arrival.id_platform == ship_id,\
#             Transect.arrival.port.id.in_(stop_ids)).order_by(Transect.arrival.event_time.asc())
        stop = query.first()
        if start and stop:
            route_lst = filter(lambda x: (x.id_start == start.departure.port.id) and 
                               (x.id_stop == stop.arrival.port.id), route_lst)
        else:
            route_lst = []
        if len(route_lst) > 1:
            log.error('too many matching routes', platform=transect.platform.code, transect_id=transect.id) 
        route = None
        if len(route_lst) == 1:
            route = route_lst[0]
        return(route)

