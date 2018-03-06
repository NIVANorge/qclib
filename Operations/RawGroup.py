"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Operations.MergeRawLog
===========================



(C) 5. okt. 2016 Pierre Jaccard
"""
import os
import math

import numpy as np

from pyTools.Navigation import tll2mps
from pyTools.Navigation import ll2crs
from pyTools.NumPy import Interpolate
from pyTools.NumPy import blocks
from pyTools.netCDF.ncOperations import ncMerge
from pyTools.netCDF.ncOperations import ncClean


from .. import Globals
from ..netCDF import Generic
from ..netCDF import Data
from ..netCDF import Flags
from ..netCDF.ncOperations import copyVariable
from ..Database import PoolDB
from ..Database import EventDB
from .. import Loggers
from .. import FolderManagers

from .BaseOperations import PoolOperation
from .BaseOperations import OpBasedOperation
from pyTools.Conversions import day1950_to_datetime
from pyTools.Conversions import datetime_to_day1950

log = Loggers.getLogger(__name__)

class RawCombiner(PoolOperation):
    
    TRIGGER_STATUS = Globals.FileStatus.NEW_RAW_DATA_
    OPERATION_NAME = Globals.Operations.COMBINE_RAW_DATA_
    RESULT_STATUS  = Globals.FileStatus.NEW_RAW_DATA_FERRYBOX
    
    def __init__(self, fm, ncf):
        super(RawCombiner, self).__init__(ncf, fm)
        try:
            self.gsrc = self.ncobj.findGroup('/raw/' + fm['nc_group'])
        except Exception as err:
            pass
        self.gdst = self.ncobj.findGroup('/raw/ferrybox')
        return
            
    @classmethod
    def todoList(cls, **kw):    
        db   = PoolDB.PoolDB()
        st_lst = db.list(PoolDB.Schema.StatusCode, code=cls.TRIGGER_STATUS + '%')
        st_lst = filter(lambda x: x.code != cls.TRIGGER_STATUS, st_lst)
        st_lst = filter(lambda x: x.code != Globals.FileStatus.NEW_RAW_DATA_FERRYBOX, st_lst)
        rlst = []
        for st_rec in st_lst:
            grp  = st_rec.code.split('_')[-1]
            stid = cls.TRIGGER_STATUS + grp
            opid = cls.OPERATION_NAME + grp
            rlst += db.todoListByOp(opid, stid)
        db.close()
        return(rlst)
                
    def merge(self, ncf, fm, *args):
        log.enter('preparing merge', file=ncf, group=self.gsrc.path)
        try:
            prefix = fm['nc_group']
            tmpf   = os.path.join(fm.path, 'idata.nc')
            if os.path.exists(tmpf):
                os.unlink(tmpf)
            nctmp = Generic.netCDF(tmpf)
            gtmp  = nctmp.createPath(self.gdst.path)
            log.info('tmp results in file %s', tmpf)
            nlst  = filter(lambda x: x.isupper(), self.gsrc.variables.keys())
            vlst  = []
            for nsrc in nlst:
                if not nsrc.startswith(prefix):
                    ndst = prefix + '_' + nsrc
                else:
                    ndst = nsrc
                vsrc = self.gsrc.variables[nsrc]
                if len(vsrc.dimensions) == 1:
                    copyVariable(vsrc, gtmp, name=ndst)
                    vlst.append((nsrc, ndst))
            log.success('found %-d variables to merge', len(vlst))
        except Exception as err:
            log.failed(err)
            raise(err)
        log.enter('interpolating data')
        try:
            tsrc = self.gsrc.variables['time']
            dt   = np.diff(tsrc[:])
            if np.any(dt < 0):
                raise ValueError('time in %s is not sorted', self.gsrc.path)
            ttmp = copyVariable(tsrc, gtmp)
            ttmp[:] = self.gdst.variables['time'][:]
            dt   = np.diff(ttmp[:])
            if np.any(dt < 0):
                raise ValueError('time in %s is not sorted', self.gdst.path)
            data = np.zeros([len(tsrc[:]), len(vlst)], dtype=np.float64)
            for i in range(len(vlst)):
                nsrc = vlst[i][0]
                data[:,i] = self.gsrc.variables[nsrc][:]
            idata = Interpolate.interp1d(ttmp[:], tsrc[:], data)
            for i in range(len(vlst)):
                ndst = vlst[i][1]
                gtmp.variables[ndst][:] = idata[:,i]
            log.success('interpolated %-d data', np.size(idata,0))
        except Exception as err:
            log.failed(err)
            raise(err)
        log.enter('merging results to original file')
        try:
            for v in vlst:
                vname = v[1]
                vtmp  = gtmp.variables[vname]
                if vname not in self.gdst.variables:
                    vdst = copyVariable(vtmp, self.gdst)
                else:
                    vdst = self.gdst.variables[vname]
                vdst[:] = vtmp[:]
            self.ncobj.close()
            nctmp.close()
            log.success()
#             dopts = { 'index': np.arange(len(ttmp)) }
#             mvar  = self.gdst.path + '/time'
#             self.ncobj.close()
#             nctmp.close()
#             ncMerge.file(tmpf, self.file, merge_var=mvar, dopts=dopts)
#            log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        return
       
    @classmethod
    def process(cls, ncf, fm, *args):
        obj  = cls(fm, ncf)
        if obj.gdst is None:
            log.info('skipping, no ferrybox data')
            obj = None
        else:
            obj.merge(ncf, fm)
            db = PoolDB.PoolDB()
            db.register_raw_file(fm['nc_source'], cls.RESULT_STATUS)
            db.close()
        return(obj)

class UpdateNavigation(PoolOperation):

    TRIGGER_STATUS = Globals.FileStatus.NEW_RAW_DATA_FERRYBOX
    OPERATION_NAME = Globals.Operations.UPDATE_NAVIGATION
    RESULT_STATUS  = Globals.FileStatus.NEW_NAV_DATA
               
    def shipSpeed(self):
        fb  = Data.RawFerrybox(self.ncobj._nc)
        try:
            fb.chdir()
        except:
            return
        iall = np.argsort(fb.time[:])
        mps = tll2mps(fb.time[iall]*86400.0, fb.GPS_LONGITUDE[iall], fb.GPS_LATITUDE[iall])
        if 'SHIP_SPEED' not in fb:        
            fb.createVariable(fb.chdir(), 'SHIP_SPEED', 'm/s', np.float64, np.nan, fb.time.dimensions)
        v = fb.SHIP_SPEED
        v[:] = mps
        return

    def shipCourse(self):
        fb  = Data.RawFerrybox(self.ncobj._nc)
        try:
            fb.chdir()
        except:
            return
        iall = np.argsort(fb.time[:])
        crs = ll2crs(fb.GPS_LONGITUDE[iall], fb.GPS_LATITUDE[iall])
        if 'SHIP_COURSE' not in fb:        
            fb.createVariable(fb.chdir(), 'SHIP_COURSE', 'degN', np.float64, np.nan, fb.time.dimensions)
        v = fb.SHIP_COURSE
        v[:] = crs
        return
        
    @classmethod
    def process(cls, ncf, fm, *args):
        obj  = cls(ncf, fm)        
        obj.shipSpeed()
        obj.shipCourse()
        return(True)
        
class RTQC(PoolOperation):

    TRIGGER_STATUS = Globals.FileStatus.NEW_NAV_DATA
    OPERATION_NAME = Globals.Operations.APPLY_RTQC
    RESULT_STATUS  = Globals.FileStatus.NEW_RTQC_FLAGS
           
    @classmethod
    def process(cls, ncf, fm, *args):
        log.enter('apllying RTQC', file=ncf)
        try:
            fb = Data.RawFerrybox(ncf)
            assert len(fb.chdir().variables.keys()) > 0, 'No ferrybox data in file'
            fb.close()
        except:
            return(True)
    #         fb = Data.RawFerrybox(ncf)
    #         provider = fb.provider
    #         platform = fb.platform
    #         t1 = datetime.date(fb.day, Globals.D_FORMAT_USR)
    #         t0 = t1 - datetime.timedelta(days=1)
    #         f0 = fb.ncFile(provider, platform, d0)
        try:       
            Flags.RTQC_SHIP_SPEED_TEST(ncf).qc()
            Flags.RTQC_SHIP_SPEED_FROZEN_TEST(ncf).qc()
            Flags.RTQC_PUMP_TEST(ncf).qc()
            Flags.RTQC_OBSTRUCTION_TEST(ncf).qc()
            Flags.RTQC_PUMP_HISTORY_TEST(ncf).qc()
            Flags.RTQC_OBSTRUCTION_HISTORY_TEST(ncf).qc()
            Flags.RTQC_TEMPERATURE_TESTS(ncf).qc(-2.5, 40.0)
            Flags.RTQC_SALINITY_TESTS(ncf).qc()
            Flags.RTQC_CHLA_FLUORESCENCE_TESTS(ncf).qc()
            Flags.RTQC_CDOM_FLUORESCENCE_TESTS(ncf).qc()
            Flags.RTQC_TURBIDITY_TESTS(ncf).qc()
            log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        return(True)
        
class ScanForPortEvents(PoolOperation):
    
    TRIGGER_STATUS = Globals.FileStatus.NEW_NAV_DATA
    OPERATION_NAME = Globals.Operations.SCAN_FOR_PORT_EVENTS
    RESULT_STATUS  = Globals.FileStatus.NEW_PORT_EVENTS
  

    @classmethod
    def register_event(cls, fb, i, etype):
        db = EventDB.EventDB()
        t  = day1950_to_datetime(fb.time[i]).tolist()
        o  = {}
        o['id_type']     = db.register_event_type(etype)
        o['id_platform'] = db.register_platform(fb.platform)
        o['id_provider'] = db.register_provider(fb.provider)
        o['id_port']     = db.find_port(fb.GPS_LONGITUDE[i], fb.GPS_LATITUDE[i]).id
        o['latitude']    = fb.GPS_LATITUDE[i]        
        o['longitude']   = fb.GPS_LONGITUDE[i]
        eid = db.register_event(t, **o)
        bad_id = db.unknown_port().id
        if o['id_port'] == bad_id:
            db.register_unknown_position(eid, lon=fb.GPS_LONGITUDE[i], lat=fb.GPS_LATITUDE[i])
        db.close()
        log.info('new event', time=t, **o)
        return
    
    @classmethod
    def register_arrival(cls, fb, i):
        cls.register_event(fb, i, Globals.EventTypes.ARRIVAL)
        return      

    @classmethod
    def register_departure(cls, fb, i):
        cls.register_event(fb, i, Globals.EventTypes.DEPARTURE)
        return      
                
    @classmethod
    def process(cls, ncf, fm, *args):
        log.enter('checking data file', file=ncf)
        try:
            fb = Data.RawFerrybox(ncf)
            assert len(fb.chdir().variables.keys()) > 0, 'No ferrybox data in file'
            fb.close()
            log.success()
        except:
            log.failed()
            return(True)
        log.enter('scanning for new port events', file=ncf)
        try:
            fb   = Data.RawFerrybox(ncf)
            iarg = np.argsort(fb.time[:])
            time = fb.time[iarg].data
            spd  = fb.SHIP_SPEED[iarg].data
            good = ~fb.SHIP_SPEED[iarg].mask
            test = (spd[good] < 0.25)
            if not np.any(test):
                fb.close()
                log.warning('no ship speed below threshold', file=ncf)
                return(True)
            blks = blocks.blocks(test)
            ii   = np.arange(len(spd)) 
            blks[:,0] = ii[good][blks[:,0]]
            blks[:,1] = ii[good][blks[:,1]]
            blks[0,0] = 0
            blks[-1,1] = len(fb.time[:]) - 1
            done = False
            while not done:
                nblk = np.shape(blks)[0]
                dt   = (time[blks[:,1]] - time[blks[:,0]])*1440.0
                ii   = np.arange(1, nblk-1)
                idx  = np.where((dt[ii] < 5.0))[0] + 1
                if len(idx):
                    i = idx[0]
                    blks[i-1,1] = blks[i+1,1]
                    ii = np.concatenate((np.arange(0,i), np.arange(i+2,nblk)))
                    blks = blks[ii,:]
                else:
                    done = True
            for i in range(nblk):
                if blks[i,0] > 0:
                    if blks[i,2]:
                        cls.register_arrival(fb, blks[i,0])
                    else:
                        cls.register_departure(fb, blks[i,0])
            fb.close()
            log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        return(True)

class ScanForTransects(OpBasedOperation):
    
    OPERATION_NAME = Globals.Operations.SCAN_FOR_TRANSECTS
    
    @classmethod
    def todoList(cls):
        edb = EventDB.EventDB()
        pdb = PoolDB.PoolDB()
        id_op   = pdb.get_insert(PoolDB.Schema.OperationCode, code=cls.OPERATION_NAME).id
        last_op = pdb.last(PoolDB.Schema.Operation, id_operation=id_op)
        if not last_op:
            evt  = edb.first(EventDB.Schema.EventType, code=Globals.EventTypes.DEPARTURE)
            rlst = edb.fetch(EventDB.Schema.Event, id_type=evt.id)
        else:
            rlst = edb.new_departures(last_op.time)
        rlst = map(lambda x: x.id, rlst)
        edb.close()
        pdb.close()
        return(rlst)
        
    @classmethod
    def process(cls, id_dep):
        db  = EventDB.EventDB()
        dep = db.first(EventDB.Schema.Event, id=id_dep) 
        cdict = { 'provider': dep.provider.code, 'platform': dep.platform.code }
        log.enter('searching for new transects', **cdict)
        try:
            bad  = db.first(EventDB.Schema.EventType, code=Globals.EventTypes.UNKNOWN)
            bev  = db.first(EventDB.Schema.Event, id_type=bad)
            if bev:
                raise ValueError('there are unprocessed unknown events')
            idt  = db.first(EventDB.Schema.EventType, code=Globals.EventTypes.ARRIVAL)
            ign  = db.ignored_port()
            opts = { 'id_provider': dep.id_provider, 'id_platform': dep.id_platform }
            arr  = None
            rec  = dep
            test = True
            done = False
            while not done:
                rec = db.next_event(rec.event_time, **opts)
                if not rec:
                    done = True
                elif (rec.id_port == ign.id):
                    continue
                elif (rec.id_type == idt.id):
                    arr  = rec
                    done = True
            if arr:
                pool = FolderManagers.PoolRoot()
                clst = pool.cnames_from_dict(cdict)
                pdir = pool.bottom(*clst)
                t0   = datetime_to_day1950(dep.event_time)
                t1   = datetime_to_day1950(arr.event_time)
                prev = None
                now  = t0
                while now < t1:
                    ncb  = Generic.netCDF.ncFile(cdict['provider'], cdict['platform'], day1950_to_datetime(now))
                    if not pool.inPool(ncb, *clst):
                        test = False
                    else:
                        fsrc = os.path.join(pdir.path, ncb)
                        opts = { 'working_copy': True, 'working_folder': None, 'version': False }
                        with pool.lock(fsrc, **opts) as ncf:
                            fb = Data.RawFerrybox(ncf, read_only=True)
                            try:
                                fb.chdir()
                            except:
                                log.warning('no ferrybox data in file', file=ncb)
                                test = False
                            else:
                                idx = np.argsort(fb.time[:])
                                ii  = (fb.time[idx] >= now) & (fb.time[idx] <= t1)
                                t   = fb.time[idx][ii]
                                if prev is not None:
                                    t = np.insert(t, 0, [ prev ])
                                dt  = np.diff(t)*1440.0  
                                med = np.median(dt)
                                jj  = (dt > med*10)
                                if np.any(jj):
                                    test = False
                                prev = t[-1]
                            fb.close()
                    if not test:
                        break
                    now = math.floor(now) + 1.0
                if test:
                    r = db.register_transect(dep, arr)
                    log.info('registering new transect', id=r.transect_id)
            log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        finally:
            db.close()            
        return
        
        
                
    
    
            
    
    