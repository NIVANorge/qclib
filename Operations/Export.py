"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Operations.Extract
===========================



(C) 19. okt. 2016 Pierre Jaccard
"""

import os
import csv
import math
import re

import numpy as np

from pyTools.Conversions import day1950_to_datetime, datetime_to_day1950
from pyTools.FTP import FTPObject
from pyTools.Compression import gz
from pyTools import system

from .. import Globals
from .. import ConfigManager
from .. import Loggers
from ..Database import PoolDB
from ..Database import EventDB
from ..netCDF import Generic
from ..FolderManagers import PoolRoot
from ..netCDF import Data
from ..netCDF import Flags
from ..NIVABASE import IOF

from . import BaseOperations

log = Loggers.getLogger(__name__)

class FlagsOperation(object):
    
    @classmethod
    def subset(cls, flags_group, subset_name):
        g = flags_group.chdir()
        flags = g.groups[subset_name].variables.values()
        good  = flags_group.good(*flags)
        return(good)
    
    @classmethod
    def combine(cls, *flags):
        good = flags[0]
        for i in range(1,len(flags)):
            good = np.logical_and(good, flags[i])
        return(good)
    
class RTQCFlags(object):
    
    @classmethod
    def location(cls, nc):
        fsys = FlagsOperation.subset(Flags.RTQC_FLAGS(nc), 'SYSTEM')
        fnav = FlagsOperation.subset(Flags.RTQC_FLAGS(nc), 'NAVIGATION')
        good = np.logical_and(fsys, fnav)
        return(good)
    
    @classmethod
    def variable(cls, nc, var_name):
        floc = cls.location(nc)
        fvar = FlagsOperation.subset(Flags.RTQC_FLAGS(nc), var_name)
        good = np.logical_and(floc, fvar)
        return(good)
        
class ExportCSV(object):
    
    DELIMITER = ';'
    LINE_TERM = "\n"
    COMMENT   = '#'
    
    def __init__(self, fdout, ncobj, fields, **kw):
        self.fdout  = fdout
        self.ncobj  = ncobj
        self.fields = fields
        self.ncvars = self.data_objects()
        self.flst   = map(lambda x: x[0], fields)
        self.csvobj = csv.DictWriter(self.fdout, self.flst, delimiter=self.DELIMITER, lineterminator=self.LINE_TERM)
        return
    
    def header(self):
        node = self.ncobj.chdir()
        hdr  = []
        for f,d in self.fields:
            if 'var' in d:
                hdr.append(f + ' [' + node.variables[d['var']].unit + ']')
            elif 'flag' in d:
                hdr.append(f)
        self.fdout.write(self.DELIMITER.join(hdr) + self.LINE_TERM)
        return(hdr)

    def data_objects(self):
        data = []
        node = self.ncobj.chdir()
        for f,d in self.fields:
            if 'var' in d:
                data.append(node.variables[d['var']])
            elif 'flag' in d:
                data.append(d['flag'](self.ncobj._nc))
        return(data)

    @classmethod
    def add_meta(cls, fdout, *args, **kw):
        d = {}
        for a in args:
            d.update(a)
        d.update(kw)
        klst = sorted(d.keys())
        lmax = max(map(lambda x: len(x), klst))
        for i in range(len(klst)):
            k = klst[i]
            s = k + ' '*(lmax-len(k))
            fdout.write(cls.COMMENT + ' ' + s + ': ' + d[k] + cls.LINE_TERM)
        return
                
    def export_one(self, idx):
        ii = range(len(self.flst))
        d  = filter(lambda j: self.ncvars[j][:][idx] is np.ma.masked, ii)
        if len(d) > 0:
            return(None)
        d = map(lambda j: self.fields[j][1]['str'](self.ncvars[j][:][idx]), ii)
        d = dict(zip(self.flst, d))
        self.csvobj.writerow(d)
        return(d)
    
    def export_many(self, condition):
        cnt  = 0
        ii   = range(len(self.flst))
        data = map(lambda j: self.ncvars[j][:][:], ii)
        d    = dict(zip(self.flst, data))
        ii   = condition(d)
        for i in ii:
            n = self.export_one(i)
            if n:
                cnt += 1
        return(cnt)

    @classmethod
    def export_nc(cls, fdout, fsrc, fields, condition, **kw):
        if ('nc_class' not in kw) or (not kw['nc_class']):
            kw['nc_class'] = Data.RawFerrybox
        pool = PoolRoot()
        if not os.path.exists(fsrc):
            raise IOError('file not found: %s', fsrc)
        opts = { 'working_copy': True, 'working_folder': None, 'version': False }
        for k in opts:
            if (k in kw) and (kw[k] is not None):
                opts[k] = kw[k]
        with pool.lock(fsrc, **opts) as ncf:
            fb = kw['nc_class'](ncf, read_only=True)
            try:
                fb.chdir()
            except:
                raise ValueError('no data in file: %s', ncf)
            xobj = cls(fdout, fb, fields)
            if ('write_header' in kw) and kw['write_header']:
                xobj.header()
            n = xobj.export_many(condition)
            fb.close()
        return(n)
    
            
            
        
    

class ExportSSRDV(BaseOperations.PoolOperation):

    OPERATION_NAME = Globals.Operations.EXTRACT_SSRDV
    TRIGGER_STATUS = Globals.FileStatus.NEW_RTQC_FLAGS
    RESULT_STATUS  = Globals.FileStatus.SSRDV_EXTRACTED

    FIELDS = (('TIME', 
                    {'var': 'time', 
                     'str' : lambda x: day1950_to_datetime(x).strftime(Globals.DT_FORMAT_ISO) }),
              ('LONGITUDE',
                    {'var': 'GPS_LONGITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('LATITUDE',
                    {'var': 'GPS_LATITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('SYSTEM_FLAG',
                    {'flag': lambda x: FlagsOperation.subset(Flags.RTQC_FLAGS(x), 'SYSTEM'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('NAVIGATION_FLAG',
                    {'flag': lambda x: FlagsOperation.subset(Flags.RTQC_FLAGS(x), 'NAVIGATION'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('TEMPERATURE',
                    {'var': 'INLET_TEMPERATURE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('TEMPERATURE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'INLET_TEMPERATURE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('SALINITY',
                    {'var': 'CTD_SALINITY', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('TURBIDITY',
                    {'var': 'TURBIDITY', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('CHLA_FLUORESCENCE',
                    {'var': 'CHLA_FLUORESCENCE', 
                     'str': lambda x: '{:>12.4f}'.format(x) })
              )
  
    
    def __init__(self):
        self.odir = ConfigManager.abspath(ConfigManager.sysconf['export']['ssrdv'])
        if not os.path.exists(self.odir):
            os.makedirs(self.odir)
        self.db = PoolDB.PoolDB()        
        return
    
    def close(self):
        self._close_(self)
        return
        
    @classmethod
    def _close_(cls, obj):
        if obj.db:
            obj.db.close()
            obj.db = None
        return

    def _del_(self):
        self._close_(self)
        return
            
    def export_one(self, ncfile):
        csvb  = os.path.splitext(os.path.basename(ncfile))[0]
        csvf  = os.path.join(self.odir, csvb + '.csv')
        fd    = open(csvf, 'w')
        fb    = Data.RawFerrybox(ncfile)
        node  = fb.chdir()
        data  = []
        hdr   = []
        for f,d in self.FIELDS:
            if 'var' in d:
                data.append(node.variables[d['var']])
                hdr.append(f + ' [' + node.variables[d['var']].unit + ']')
            elif 'flag' in d:
                data.append(d['flag'](fb._nc))
                hdr.append(f)
        flst  = map(lambda x: x[0], self.FIELDS)
        jj    = range(len(flst))
        count = 0
        #
        log.enter('exporting CSV data')
        try:
            o = csv.DictWriter(fd, flst, delimiter=';', lineterminator="\n")
            fd.write(';'.join(hdr) + "\n")
            for i in range(len(fb.time[:])):
                d = map(lambda j: self.FIELDS[j][1]['str'](data[j][:][i]), jj)
                d = dict(zip(flst, d))
                o.writerow(d)
                count += 1
            log.success(count=count, csv=csvf)
        except Exception as err:
            log.failed(err, count=count, csv=csvf)
            raise(err)
        finally:
            fd.close()
        return(csvf)
    
    @classmethod
    def process(cls, ncf, fm, *args):
        log.enter('exporting SSRDV csv file', file=ncf)
        try:
            obj = cls()
            csvf = obj.export_one(ncf)
            log.success(csv=csvf)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(True)

    @classmethod
    def execute(cls, *args, **kw):
        lopts = { 'version': False }
        kw['lopts'] = lopts
        super(ExportSSRDV, cls).execute(*args, **kw)
        return

class ExportJERICO(BaseOperations.PoolOperation):

    OPERATION_NAME = Globals.Operations.EXTRACT_JERICO
    TRIGGER_STATUS = Globals.FileStatus.NEW_RTQC_FLAGS
    RESULT_STATUS  = Globals.FileStatus.JERICO_EXTRACTED

    HEADER = """
            # DISCLAIMER
            # These data are freely distributed by NIVA (www.niva.no) through the supporting
            # funds from JERICO-NEXT. They are provided as is. By opening this file you agree
            # to use them in a constructive way and include the reference below to all of your 
            # work using these data directly or indirectly.
            #
            # Project       : JERICO-NEXT
            # Projet Contact: Andrew King (aki@niva.no)
            # File Author   : Pierre Jaccard (pja@niva.no)
            # Flags Meaning : 0=failed, 1=passed
            # Data Provider : Norwegian Instititute for Water Research (NIVA) 
            # Provider URL  : www.niva.no
            # Data URL      : www.ferrybox.no
            # Platform      : {platform}
            # Reference     : Data from Ferrybox platform {platform} provided freely by NIVA (www.niva.no)
"""
    FIELDS = (('TIME', 
                    {'var': 'time', 
                     'str' : lambda x: day1950_to_datetime(x).strftime(Globals.DT_FORMAT_ISO) }),
              ('LONGITUDE',
                    {'var': 'GPS_LONGITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('LATITUDE',
                    {'var': 'GPS_LATITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('SYSTEM_FLAG',
                    {'flag': lambda x: RTQCFlags.location(x), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('TEMPERATURE',
                    {'var': 'INLET_TEMPERATURE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('TEMPERATURE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'INLET_TEMPERATURE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('SALINITY',
                    {'var': 'CTD_SALINITY', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('SALINITY_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CTD_SALINITY'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('CHLA_FLUORESCENCE',
                    {'var': 'CHLA_FLUORESCENCE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('CHLA_FLUORESCENCE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CHLA_FLUORESCENCE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              )
  
  
    
    def __init__(self):
        self.odir = ConfigManager.abspath(ConfigManager.sysconf['export']['jerico'])
        if not os.path.exists(self.odir):
            os.makedirs(self.odir)
        self.db = PoolDB.PoolDB()  
        self.ftp  = FTPObject(**ConfigManager.sysconf['ftp']['jerico'])
        return
    
    def close(self):
        self._close_(self)
        return
        
    @classmethod
    def _close_(cls, obj):
        if obj.db:
            obj.db.close()
            obj.db = None
        return

    def _del_(self):
        self._close_(self)
        return

    @classmethod
    def todoList(cls, **kw):
        rlst = super(ExportJERICO, cls).todoList(**kw)
        func = lambda x: re.search('^NIVA_[^_]+_(2016|2017)-.+\.nc$', x)
        rlst = filter(lambda x: func(x['file']), rlst)
        return(rlst)

            
    def export_one(self, ncfile):
        csvb  = os.path.splitext(os.path.basename(ncfile))[0]
        csvf  = os.path.join(self.odir, csvb + '.csv')
        fd    = open(csvf, 'w')
        fb    = Data.RawFerrybox(ncfile)
        node  = fb.chdir()
        head  = self.HEADER.format(platform=fb._nc.platform)
        head  = head.splitlines()
        head  = map(lambda x: x.strip(), head)
        fd.write('\n'.join(head) + "\n")
        data = []
        hdr  = []
        for f,d in self.FIELDS:
            if 'var' in d:
                data.append(node.variables[d['var']])
                hdr.append(f + ' [' + node.variables[d['var']].unit + ']')
            elif 'flag' in d:
                data.append(d['flag'](fb._nc))
                hdr.append(f)
        flst  = map(lambda x: x[0], self.FIELDS)
        good  = RTQCFlags.location(fb._nc)
        jj    = range(len(flst))
        count = 0
        #
        log.enter('exporting CSV data')
        try:
            o = csv.DictWriter(fd, flst, delimiter=';', lineterminator="\n")
            fd.write(';'.join(hdr) + "\n")
            for i in range(len(fb.time[:])):
                if not good[i]:
                    continue
                d = map(lambda j: self.FIELDS[j][1]['str'](data[j][:][i]), jj)
                d = dict(zip(flst, d))
                o.writerow(d)
                count += 1
            log.success(count=count, csv=csvf)
        except Exception as err:
            log.failed(err, count=count, csv=csvf)
            raise(err)
        finally:
            fd.close()
        return(csvf)
    
    @classmethod
    def process(cls, ncf, fm, *args):
        b = os.path.basename(ncf)
        d = b.split('_')[2]
        y = d.split('-')[0]
        if y not in [ '2016', '2017' ]:
            return(False)
        log.enter('exporting JERICO csv file', file=ncf)
        try:
            obj = cls()
            csvf = obj.export_one(ncf)
            log.enter('compressing JERICO file %s', csvf)
            try:
                gz_file = gz.compress(csvf, delete=True)
                log.success(gzfile=gz_file)
            except Exception as err:
                log.failed(err)
                raise(err)        
            log.enter('uploading JERICO file to FTP')
            try:
                obj.ftp.connect()
                obj.ftp.put(gz_file, os.path.basename(gz_file))
                obj.ftp.quit()
                log.success()
            except Exception as err:
                log.failed(err)
                raise(err)        
            log.success(csv=csvf)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(True)

    @classmethod
    def execute(cls, *args, **kw):
        lopts = { 'version': False }
        kw['lopts'] = lopts
        super(ExportJERICO, cls).execute(*args, **kw)
        return
        
class ExportIndreOsloFjord(BaseOperations.PoolOperation):

    OPERATION_NAME = Globals.Operations.EXTRACT_IOF
    TRIGGER_STATUS = Globals.FileStatus.NEW_RTQC_FLAGS
    RESULT_STATUS  = Globals.FileStatus.IOF_EXTRACTED

    FIELDS = (('TIME', 
                    {'var': 'time', 
                     'str' : lambda x: day1950_to_datetime(x).strftime(Globals.DT_FORMAT_ISO) }),
              ('LONGITUDE',
                    {'var': 'GPS_LONGITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('LATITUDE',
                    {'var': 'GPS_LATITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('SYSTEM_FLAG',
                    {'flag': lambda x: RTQCFlags.location(x), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('TEMPERATURE',
                    {'var': 'INLET_TEMPERATURE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('TEMPERATURE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'INLET_TEMPERATURE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('SALINITY',
                    {'var': 'CTD_SALINITY', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('SALINITY_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CTD_SALINITY'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('CHLA_FLUORESCENCE',
                    {'var': 'CHLA_FLUORESCENCE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('CHLA_FLUORESCENCE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CHLA_FLUORESCENCE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('CDOM_FLUORESCENCE',
                    {'var': 'CDOM_FLUORESCENCE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('CDOM_FLUORESCENCE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CDOM_FLUORESCENCE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('TURBIDITY',
                    {'var': 'TURBIDITY', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('TURBIDITY_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'TURBIDITY'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              )
  
    
    def __init__(self):
        self.odir = ConfigManager.abspath(ConfigManager.sysconf['export']['iof'])
        if not os.path.exists(self.odir):
            os.makedirs(self.odir)
        self.db = PoolDB.PoolDB()        
        return
    
    def close(self):
        self._close_(self)
        return
        
    @classmethod
    def _close_(cls, obj):
        if obj.db:
            obj.db.close()
            obj.db = None
        return

    def _del_(self):
        self._close_(self)
        return
            
    def export_one(self, ncfile):
        try:
            fb = Data.RawFerrybox(ncfile)
            assert fb.platform == 'FA', 'not the correct platform'
            assert len(fb.chdir().variables.keys()) > 0, 'no data'
        except Exception as err:
            return(str(err))
        csvb  = os.path.splitext(os.path.basename(ncfile))[0]
        csvf  = os.path.join(self.odir, csvb + '.csv')
        fd    = open(csvf, 'w')
        fb    = Data.RawFerrybox(ncfile)
        node  = fb.chdir()
        data  = []
        hdr   = []
        for f,d in self.FIELDS:
            if 'var' in d:
                data.append(node.variables[d['var']])
                hdr.append(f + ' [' + node.variables[d['var']].unit + ']')
            elif 'flag' in d:
                data.append(d['flag'](fb._nc))
                hdr.append(f)
        flst  = map(lambda x: x[0], self.FIELDS)
        jj    = range(len(flst))
        count = 0
        #
        log.enter('exporting data CSV and NIVABASE')
        try:
            db = IOF.Database()
            o  = csv.DictWriter(fd, flst, delimiter=';', lineterminator="\n")
            fd.write(';'.join(hdr) + "\n")
            for i in range(len(fb.time[:])):
                if fb.GPS_LATITUDE[:][i] < 59.65:
                    continue
                d = filter(lambda j: data[j][:][i] is np.ma.masked, jj)
                if len(d) > 0:
                    continue
                #
                d  = map(lambda j: data[j][:][i], jj)
                kk = filter(lambda x: d[x].dtype == np.bool, range(len(d)))
                for k in kk:
                    d[k] = int(d[k])
                d = dict(zip(flst, d))
                d['TIME'] = day1950_to_datetime(d['TIME'])                
                dbid = db.insert_record(d)
                #
                d = map(lambda j: self.FIELDS[j][1]['str'](data[j][:][i]), jj)
                d = dict(zip(flst, d))
                o.writerow(d)
                #
                count += 1
            log.success(count=count, csv=csvf)
        except Exception as err:
            log.failed(err, count=count, csv=csvf)
            raise(err)
        finally:
            db.close()
            fd.close()
        #
    
    @classmethod
    def process(cls, ncf, fm, *args):
        log.enter('exporting IOF csv file', file=ncf)
        try:
            obj = cls()
            csvf = obj.export_one(ncf)
            log.success(csv=csvf)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(True)

    @classmethod
    def execute(cls, *args, **kw):
        lopts = { 'version': False }
        kw['lopts'] = lopts
        super(ExportIndreOsloFjord, cls).execute(*args, **kw)
        return

class ExportCMEMS(BaseOperations.OpBasedOperation):

    OPERATION_NAME = Globals.Operations.EXTRACT_CMEMS

    FIELDS = (('TIME', 
                {'var' : 'time', 
                 'unit': 'datetime in ISO format YYYYmmddTHHMMSSZ',
                 'str' : lambda x: day1950_to_datetime(x).strftime(Globals.DT_FORMAT_ISO) }),
#               ('TIME', 
#                     {'var': 'time', 
#                      'str' : lambda x: '{:>12.6f}'.format(x) }),
              ('LONGITUDE',
                    {'var': 'GPS_LONGITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('LATITUDE',
                    {'var': 'GPS_LATITUDE', 
                     'str': lambda x: '{:>12.6f}'.format(x) }),
              ('SYSTEM_FLAG',
                    {'flag': lambda x: RTQCFlags.location(x), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('TEMPERATURE',
                    {'var': 'INLET_TEMPERATURE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('TEMPERATURE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'INLET_TEMPERATURE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('SALINITY',
                    {'var': 'CTD_SALINITY', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('SALINITY_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CTD_SALINITY'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              ('CHLA_FLUORESCENCE',
                    {'var': 'CHLA_FLUORESCENCE', 
                     'str': lambda x: '{:>12.4f}'.format(x) }),
              ('CHLA_FLUORESCENCE_FLAG',
                    {'flag': lambda x: RTQCFlags.variable(x, 'CHLA_FLUORESCENCE'), 
                     'str' : lambda x: '{:01d}'.format(int(x)) }),
              )
  
    
    def __init__(self):
        self.odir = ConfigManager.abspath(ConfigManager.sysconf['export']['cmems'])
        if not os.path.exists(self.odir):
            os.makedirs(self.odir)
        fcfg = os.path.join(ConfigManager.CONFIGROOT, 'export', 'cmems.ini')
        self.meta = ConfigManager.ConfigObj(fcfg)['meta']
        self.ftp  = FTPObject(**ConfigManager.sysconf['ftp']['cmems'])
        return
    
    def close(self):
        self._close_(self)
        return
        
    @classmethod
    def _close_(cls, obj):
        return

    def _del_(self):
        self._close_(self)
        return

    @classmethod
    def todoList(cls):
        edb = EventDB.EventDB()
        pdb = PoolDB.PoolDB()
        id_op   = pdb.get_insert(PoolDB.Schema.OperationCode, code=cls.OPERATION_NAME).id
        last_op = pdb.last(PoolDB.Schema.Operation, id_operation=id_op)
        if not last_op:
            rlst = edb.fetch(EventDB.Schema.Transect)
        else:
            rlst = edb.new_transects(last_op.time)
        rlst = filter(lambda x: x.departure.port.code != x.arrival.port.code, rlst)
        rlst = map(lambda x: x.id, rlst)
        edb.close()
        pdb.close()
        return(rlst)

    def output_file(self, provider, vessel, route, t_start, t_stop, p_start, p_stop):
        if isinstance(t_start, float):
            t_start = day1950_to_datetime(t_start)
        if isinstance(t_stop, float):
            t_stop = day1950_to_datetime(t_stop)        
        f = [ provider.upper(), vessel.upper() ]
        if route:
            f += [ route.start.code, route.stop.code ]
        else:
            f += [ 'X', 'Y' ]
        f += [ t_start.strftime(Globals.DT_FORMAT_ISO), p_start ]
        f += [ t_stop.strftime(Globals.DT_FORMAT_ISO) , p_stop  ]
        f = os.path.join(self.odir, '_'.join(f) + '.csv')
        f = system.String.unicode_to_ascii(f)
        return(f)
                
    def select(self, data, t0, t1):
        idx = np.argsort(data['TIME'])
        ii  = (data['TIME'][idx] >= t0) & (data['TIME'][idx] <= t1)
        ii  = idx[ii]
        return(ii)
        
    @classmethod   
    def process(cls, rec_id):
        xobj = cls()
        db   = EventDB.EventDB()
        rec  = db.first(EventDB.Schema.Transect, id=rec_id)
        log.enter('exporting CMEMS data for %s', rec.transect_id)
        try:
            pool_db  = PoolDB.PoolDB()
            provider = rec.departure.provider
            platform = rec.departure.platform
            t_dep    = rec.departure.event_time
            p_dep    = rec.departure.port.code
            t_arr    = rec.arrival.event_time
            p_arr    = rec.arrival.port.code
            pool_db  = PoolDB.PoolDB()
            ship     = pool_db.session.query(PoolDB.Schema.Platform).filter_by(code=platform.code).first()
            cdict    = { 'provider': provider.code, 'platform': platform.code }
            meta = { 
                'platform_name'    : platform.name,
                'ices_code'        : platform.ices,
                'imo_code'         : platform.imo,
                'call_sign'        : platform.sign,
                'niva_code'        : platform.code,      
                'time_of_departure': t_dep.strftime(Globals.DT_FORMAT_USR), 
                'time_of_arrival'  : t_arr.strftime(Globals.DT_FORMAT_USR),
                'time_of_transect' : '{:-.2f} hours'.format((t_arr - t_dep).total_seconds()/3600),
                'port_of_departure': rec.departure.port.code + ' [' + rec.departure.port.name + ']',
                'port_of_arrival'  : rec.arrival.port.code + ' [' + rec.arrival.port.name + ']',
                'transect_id'      : rec.transect_id,              
                }
            pool_db.close()
            route = db.find_route(rec)
            if route:
                meta['route'] = '{} to {}'.format(route.start.name, route.stop.name)
            out_file = None
            ALWAYS_EXPORT = False
            if route or ALWAYS_EXPORT: 
                pool     = PoolRoot()
                clst     = pool.cnames_from_dict(cdict)
                pdir     = pool.bottom(*clst)
                out_file = xobj.output_file(provider.code, platform.code, route, t_dep, t_arr, p_dep, p_arr)
                fd = open(out_file, 'wb')
                ExportCSV.add_meta(fd, xobj.meta, **meta)
                t0   = datetime_to_day1950(t_dep)
                t1   = datetime_to_day1950(t_arr)
                now  = t0
                ntot = 0
                while now < t1:
                    ncb = Generic.netCDF.ncFile(provider.code, platform.code, day1950_to_datetime(now))
                    ncf = os.path.join(pdir.path, ncb)
                    log.enter('adding data from file %s', ncb, **cdict)
                    try:
                        fsel = lambda x: xobj.select(x, t0, t1)
                        opts = {}
                        if now == t0:
                            opts['write_header'] = True
                        ngood = ExportCSV.export_nc(fd, ncf, cls.FIELDS, fsel, **opts)
                        ntot += ngood
                        log.success(ngood=ngood)
                    except Exception as err:
                        log.failed(err)
                        raise(err)
                    now = math.floor(now) + 1.0
                fd.close()
                log.success(output=out_file, ntot=ntot)
            else:
                log.warning('no route found')
                log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        finally:
            db.close()
        #
        if out_file is not None:
            log.enter('compressing CMEMS file %s', out_file)
            try:
                gz_file = gz.compress(out_file, delete=True)
                log.success(gzfile=gz_file)
            except Exception as err:
                log.failed(err)
                raise(err)        
        #
        if route:
            log.enter('uploading CMEMS file to FTP')
            try:
                xobj.ftp.connect()
                xobj.ftp.put(gz_file, os.path.basename(gz_file))
                xobj.ftp.quit()
                log.success()
            except Exception as err:
                log.failed(err)
                raise(err)        
        return

    @classmethod
    def execute(cls, *args, **kw):
        lopts = { 'version': False }
        kw['lopts'] = lopts
        super(ExportCMEMS, cls).execute(*args, **kw)
        return


# class ExportCMEMS(BaseOperations.OpBasedOperation):
# 
#     OPERATION_NAME = Globals.Operations.EXTRACT_CMEMS
# 
#     FIELDS = (('TIME', 
#                     {'var': 'time', 
#                      'str' : lambda x: day1950_to_datetime(x).strftime(Globals.DT_FORMAT_ISO) }),
#               ('LONGITUDE',
#                     {'var': 'GPS_LONGITUDE', 
#                      'str': lambda x: '{:>12.6f}'.format(x) }),
#               ('LATITUDE',
#                     {'var': 'GPS_LATITUDE', 
#                      'str': lambda x: '{:>12.6f}'.format(x) }),
#               ('SYSTEM_FLAG',
#                     {'flag': lambda x: RTQCFlags.location(x), 
#                      'str' : lambda x: '{:01d}'.format(int(x)) }),
#               ('TEMPERATURE',
#                     {'var': 'INLET_TEMPERATURE', 
#                      'str': lambda x: '{:>12.4f}'.format(x) }),
#               ('TEMPERATURE_FLAG',
#                     {'flag': lambda x: RTQCFlags.variable(x, 'INLET_TEMPERATURE'), 
#                      'str' : lambda x: '{:01d}'.format(int(x)) }),
#               ('SALINITY',
#                     {'var': 'CTD_SALINITY', 
#                      'str': lambda x: '{:>12.4f}'.format(x) }),
#               ('SALINITY_FLAG',
#                     {'flag': lambda x: RTQCFlags.variable(x, 'CTD_SALINITY'), 
#                      'str' : lambda x: '{:01d}'.format(int(x)) }),
#               ('CHLA_FLUORESCENCE',
#                     {'var': 'CHLA_FLUORESCENCE', 
#                      'str': lambda x: '{:>12.4f}'.format(x) }),
#               ('CHLA_FLUORESCENCE_FLAG',
#                     {'flag': lambda x: RTQCFlags.variable(x, 'CHLA_FLUORESCENCE'), 
#                      'str' : lambda x: '{:01d}'.format(int(x)) }),
#               )
#   
#     
#     def __init__(self):
#         self.odir = ConfigManager.abspath(ConfigManager.sysconf['export']['cmems'])
#         if not os.path.exists(self.odir):
#             os.makedirs(self.odir)
#         fcfg = os.path.join(ConfigManager.CONFIGROOT, 'export', 'cmems.ini')
#         self.meta = ConfigManager.ConfigObj(fcfg)['meta']
#         self.ftp  = FTPObject(**ConfigManager.sysconf['ftp']['cmems'])
#         return
#     
#     def close(self):
#         self._close_(self)
#         return
#         
#     @classmethod
#     def _close_(cls, obj):
#         return
# 
#     def _del_(self):
#         self._close_(self)
#         return
# 
#     @classmethod
#     def todoList(cls):
#         edb = _EventDB.Database()
#         pdb = _PoolDB._PoolDB()
#         id_op   = pdb.get_insert(_PoolDB.OperationCode, code=cls.OPERATION_NAME).id
#         last_op = pdb.last(_PoolDB.Operation, id_operation=id_op)
#         if not last_op:
#             rlst = edb.fetch(_EventDB.Transect)
#         else:
#             rlst = edb.new_transects(last_op.time)
#         rlst = filter(lambda x: x.departure.port.code != x.arrival.port.code, rlst)
#         rlst = map(lambda x: x.id, rlst)
#         edb.close()
#         pdb.close()
#         return(rlst)
# 
#     def output_file(self, provider, vessel, t_start, t_stop, p_start, p_stop):
#         if isinstance(t_start, float):
#             t_start = day1950_to_datetime(t_start)
#         if isinstance(t_stop, float):
#             t_stop = day1950_to_datetime(t_stop)        
#         f = [ provider.upper(), vessel.upper() ]
#         f += [ t_start.strftime(Globals.DT_FORMAT_ISO), p_start ]
#         f += [ t_stop.strftime(Globals.DT_FORMAT_ISO) , p_stop  ]
#         f = os.path.join(self.odir, '_'.join(f) + '.csv')
#         f = system.String.unicode_to_ascii(f)
#         return(f)
#                 
#     def select(self, data, t0, t1):
#         idx = np.argsort(data['TIME'])
#         ii  = (data['TIME'][idx] >= t0) & (data['TIME'][idx] <= t1)
#         ii  = idx[ii]
#         return(ii)
#         
#     @classmethod   
#     def process(cls, rec_id):
#         xobj = cls()
#         db   = _EventDB.Database()
#         rec  = db.first(_EventDB.Transect, id=rec_id)
#         log.enter('exporting CMEMS data for %s', rec.transect_id)
#         try:
#             provider = rec.departure.provider.code
#             platform = rec.departure.platform.code
#             t_dep    = rec.departure.event_time
#             p_dep    = rec.departure.port.code
#             t_arr    = rec.arrival.event_time
#             p_arr    = rec.arrival.port.code
#             cdict    = { 'provider': provider, 'platform': platform }
#             pool     = PoolRoot()
#             clst     = pool.cnames_from_dict(cdict)
#             pdir     = pool.bottom(*clst)
#             out_file = xobj.output_file(provider, platform, t_dep, t_arr, p_dep, p_arr)
#             fd = open(out_file, 'wb')
#             meta = { 
#                 'platform'         : platform, 
#                 'time_of_departure': t_dep.strftime(Globals.DT_FORMAT_USR), 
#                 'time_of_arrival'  : t_arr.strftime(Globals.DT_FORMAT_USR),
#                 'time_of_transect' : '{:-.2f} hours'.format((t_arr - t_dep).total_seconds()/3600),
#                 'port_of_departure': rec.departure.port.code + ' [' + rec.departure.port.name + ']',
#                 'port_of_arrival'  : rec.arrival.port.code + ' [' + rec.arrival.port.name + ']',
#                 'transect_id'      : rec.transect_id,              
#                 }
#             route = db.find_route(rec)
#             if route:
#                 meta['route'] = '{} to {}'.format(route.start.code, route.stop.code)
#             ExportCSV.add_meta(fd, xobj.meta, **meta)
#             t0   = datetime_to_day1950(t_dep)
#             t1   = datetime_to_day1950(t_arr)
#             now  = t0
#             ntot = 0
#             while now < t1:
#                 ncb = Generic.netCDF.ncFile(provider, platform, day1950_to_datetime(now))
#                 ncf = os.path.join(pdir.path, ncb)
#                 log.enter('adding data from file %s', ncb, **cdict)
#                 try:
#                     fsel = lambda x: xobj.select(x, t0, t1)
#                     opts = {}
#                     if now == t0:
#                         opts['write_header'] = True
#                     ngood = ExportCSV.export_nc(fd, ncf, cls.FIELDS, fsel, **opts)
#                     ntot += ngood
#                     log.success(ngood=ngood)
#                 except Exception as err:
#                     log.failed(err)
#                     raise(err)
#                 now = math.floor(now) + 1.0
#             fd.close()
#             log.success(output=out_file, ntot=ntot)
#         except Exception as err:
#             log.failed(err)
#             raise(err)
#         finally:
#             db.close()
#         #
#         log.enter('compressing CMEMS file %s', out_file)
#         try:
#             gz_file = gz.compress(out_file, delete=True)
#             log.success(gzfile=gz_file)
#         except Exception as err:
#             log.failed(err)
#             raise(err)        
#         #
#         if route:
#             log.enter('uploading CMEMS file to FTP')
#             try:
#                 xobj.ftp.connect()
#                 xobj.ftp.put(gz_file, os.path.basename(gz_file))
#                 xobj.ftp.quit()
#                 log.success()
#             except Exception as err:
#                 log.failed(err)
#                 raise(err)        
#         return
# 
#     @classmethod
#     def execute(cls, *args, **kw):
#         lopts = { 'version': False }
#         kw['lopts'] = lopts
#         super(ExportCMEMS, cls).execute(*args, **kw)
#         return
        

     
        

