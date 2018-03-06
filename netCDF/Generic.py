"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.netCDF.Generic
===========================



(C) 28. jun. 2016 Pierre Jaccard
"""
import os
import re
import new
import datetime
import collections

import netCDF4
import numpy as np

from pyTools.Import import str2fun
from pyTools.netCDF import ncOperations

from .. import Globals

from .. import Loggers

log = Loggers.getLogger(__name__)

class MD5Data(object):
    
    @classmethod
    def size(cls, s):
        ii = range(0, len(s), 8)
        return(len(ii))
    
    @classmethod
    def num(cls, s):
        ii = range(0, len(s), 8)
        d  = np.array([0]*len(ii), dtype=np.uint32)
        for i in range(len(ii)):
            i0 = ii[i]
            i1 = i0 + 8
            d[i] = np.uint32(int(s[i0:i1], base=16))
        return(d)
    
    @classmethod
    def has(cls, nc, nums):
        mask = np.all(nc[:] == nums, axis=1)
        return(np.any(mask))
            

class netCDF(object):
    
    def __init__(self, fnc, **kw):
        self._group = '/'
        self._file  = fnc
        self._nc    = None
        if isinstance(fnc, netCDF4.Dataset):
            self._file = None
            self._nc   = fnc
        elif isinstance(fnc, netCDF):
            self._file = None
            self._nc   = fnc._nc
        else:
            self._file  = os.path.realpath(fnc)
            if ('read_only' in kw):
                if kw['read_only']:
                    self._nc = netCDF4.Dataset(self._file, mode='r')
                del kw['read_only']
            elif os.path.exists(self._file):
                self._nc = netCDF4.Dataset(self._file, mode='a')
            else:
                self._nc = netCDF4.Dataset(self._file, mode='w', format='NETCDF4')
        for k,v in kw.items():
            if k not in self._nc.ncattrs():
                self._nc.setncattr(k,v)
        return

    @classmethod
    def _delete_(cls, obj):
        if ('_nc' in obj.__dict__) and (obj.__dict__['_nc'] is not None) \
            and ('_file' in obj.__dict__) and (obj.__dict__['_file'] is not None):
            obj.__dict__['_nc'].close()            
            obj.__dict__['_nc'] = None
        return
    
    def __del__(self):
        self._delete_(self)
        return

    def close(self):
        if (self._nc is not None) and (self._file is not None):
            self._nc.close()
            self._nc = None
        return

    def cleanPath(self, path):
        if isinstance(path, list):
            path = '/'.join(path)
        plst = filter(lambda x: len(x)>0, path.split('/'))
        path = '/' + '/'.join(plst)
        return(path)

    def createPath(self, path):
        plst = filter(lambda x: len(x) > 0, path.split('/'))
        grp  = self._nc
        for p in plst:
            if p not in grp.groups:
                grp.createGroup(p)
            grp = grp.groups[p]
        return(grp)
        
    def variablePath(self, v):
        if hasattr(v, 'parent'):
            p = v.parent.path + '/' + v.name
        else:
            p = v.group().path + '/' + v.name
        return(p)
        
    def listGroups(self):
        glst = []
        todo = [ self._nc ]
        while len(todo) > 0:
            g = todo.pop()
            l = g.groups.values()
            todo += l
            glst += l
        return(glst)
        
    def findGroup(self, path):
        glst = self.listGroups()
        plst = map(lambda x: x.path, glst)
        ilst = np.array(map(lambda x: path.lower() == x.lower(), plst), dtype=np.bool)
        ilst = np.where(ilst)[0]
        if len(ilst) > 1:
            s = map(lambda x: glst[x].path, ilst)
            raise ValueError('too many paths matching %s: %s', path, ','.join(s))
        if not len(ilst):
            return(None)
        return(glst[ilst[0]])
        
    def chdir(self, path=None):
        if path is None:
            path = self._group
        lst = path.split('/')
        lst = filter(lambda x: len(x)>0, lst)
        grp = self._nc
        for g in lst:        
            grp = grp.groups[g]
        return(grp)

    def root(self):
        return(self._nc)
    
    def __getattr__(self, name):
        g  = self.chdir()
        if name in g.variables.keys():
            return(g.variables[name])
        while g is not None:
            if name in g.ncattrs():
                return(g.getncattr(name))
            g = g.parent
        raise(AttributeError, 'no attribute named %s', name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return(object.__setattr__(self, name, value))
        g  = self.chdir()
        if name in g.variables.keys():
            g.variables[name][:] = value
            return
        while g is not None:
            if name in g.ncattrs():
                g.setncattr(name, value)
                return
            g = g.parent
        g  = self.chdir()
        g.setncattr(name, value)
        return
  
    def __contains__(self, name):
        try:
            self.__getattr__(name)
            return(True)
        except:
            return(False)
        assert False, 'Unreachable code reached'

    def createSizedDimension(self, g, size):
        name = 'd_%-d' % (size)
        if not name.startswith('d_'):
            name = 'd_' + name
        if name not in g.dimensions:
            g.createDimension(name, size=size)
        return(name)
    
    def createVariable(self, g, name, unit, dtype='f8', fill=np.nan, dims=('d_time',)):
        v = None
        try:
            if name not in g.variables:
                g.createVariable(name, dtype, dims, fill_value=fill)
                g.variables[name].unit = unit
            v = g.variables[name]
        except Exception as err:
            pass
        return(v)
  
    @classmethod
    def ncFile(cls, provider, platform, day):
        if isinstance(day, datetime.datetime):
            day = day.strftime(Globals.D_FORMAT_USR)
        n = '_'.join([provider.upper(), platform.upper(), day])
        return(n + '.nc')

    @classmethod
    def ncDict(cls, ncf):
        b = os.path.splitext(os.path.basename(ncf))[0]
        w = b.split('_')
        d = { 'provider': w[0], 'platform': w[1], 'day': w[2] }
        return(d)


class LogData(netCDF):
    
    def __init__(self, fnc, conf, **kw):
        super(LogData, self).__init__(fnc, **kw)
        self._conf  = conf
        self._group = conf['ncgroup']
        path = self._group.split('/')
        g = self._nc
        for p in path:
            if p and (p not in g.groups):
                g = g.createGroup(p)
            else:
                g = g.groups[p]
        if 'd_time' not in g.dimensions:
            g.createDimension('d_time', size=None)
        if 'batch_id' not in g.variables:
            super(LogData, self).createVariable(g, 'batch_id', 'none', dtype=np.uint32, fill=0, dims=('d_time',))
        for k in self._conf.sections:
            if ('convert' in self._conf[k]) and isinstance(self._conf[k]['convert'], basestring):
                self._conf[k]['convert'] = str2fun(self._conf[k]['convert'])
        return

    def createVariable(self, grp, name, data):
        cfg = self._conf[name]
        opt = {}
        if 'nctype' in cfg:
            t = str2fun(cfg['nctype'])
        elif hasattr(data, 'dtype'):
            t = data.dtype
        else:
            t = type(data)
        if 'unit' not in cfg:
            cfg['unit'] = 'none'
        if 'ncfill' in cfg:
            if isinstance(cfg['ncfill'], basestring):
                cfg['ncfill'] = eval(cfg['ncfill'])
            opt['fill'] = cfg['ncfill']
        if isinstance(data, collections.Sized) and (len(data) > 1):
            opt['dims'] = ('d_time', self.createSizedDimension(grp, len(data)))
        try:
            super(LogData, self).createVariable(grp, name, cfg['unit'], dtype=t, **opt)
        except Exception as err:
            raise err
        return
        
#     def hasData(self, g, data):
#         test = False
#         m5n  = Globals.MD5_DATA_NAME
#         if m5n in g.variables:
#             m5v  = g.variables[m5n]
#             test = MD5Data.has(m5v, data[m5n])
#         return(test)
# 
#     def hasData(self, g, data):
#         test = map(lambda x: (x,x in g.variables), data.keys())
#         idx  = np.where(g.variables['time_id'][:] == data['time_id'])[0]
#         test = map(lambda x: (x[0],x[1] & (g.variables[x[0]][idx] == data[x[0]])), test)
#         return(dict(test))
        

    def addRecord(self, data):
        g    = self.chdir()
        vlst = data.keys()
        clst = map(lambda x: self._conf[x], vlst)
        if self._conf['time_step']:
            dts = np.uint(self._conf['time_step'])
        else:
            dts = np.uint(0)
        mask = np.ones([len(vlst)], dtype=np.bool)
        if ('time_id' in g.variables):
            vid  = g.variables['time_id']
            idx  = np.argmin(np.abs(vid[:] - data['time_id']))
            dmin = np.abs(vid[:][idx] - data['time_id'])
            mask = np.logical_and(mask, dmin > (0.5*dts))
        mask = np.logical_or(mask, map(lambda x: x not in g.variables, vlst))
        mask = np.logical_and(mask, map(lambda x: ('ignore' not in x) or (not x['ignore']), clst))
        dim  = g.dimensions['d_time']
        idx  = len(dim)
        ilst = filter(lambda x: mask[x], range(len(vlst)))
        for i in ilst:
            k = vlst[i]
            c = self._conf[k]
            if 'convert' in c:
                try:
                    d = c['convert'](data[k])
                except Exception as err:
                    log.failed(err, file=self._file, variable=k, value=d, index=idx)
                    raise err
            else:
                d = data[k]
            if k not in g.variables:
                self.createVariable(g, k, d)
            try:
                v = g.variables[k]
                v[idx] = d
            except Exception as err:
                log.failed(err, file=self._file, variable=k, value=d, index=idx)
                raise err            
        return

    def clean(self):
        g = self.chdir()
        ncOperations.ncClean.sort(g, self.time)
        return





class Flags(netCDF):
    
    _CONTEXT_NODE = None
    _GROUP_NAME   = None
    
    def __init__(self, fnc, context=None, group=None):
        super(Flags, self).__init__(fnc)
        if not context:
            context = self._CONTEXT_NODE
        self._context_node = context 
        if not group:
            group = self._GROUP_NAME
        self._group_name = group
        path = self.cleanPath([ context, '_flags', group ])
        self._group = path
        self.createPath(self._group)
        return

    def contextNode(self):
        g = self.chdir(self._context_node)
        return(g)
                
    def flag(self, ncvar, **kw):
        kw['group']  = self.__class__
        kw['subset'] = ncvar.group().path.split('/')[-1]
        f = Flag(self._nc, ncvar._name, **kw)
        return(f)

    def flags(self, dimopt=None, regex=None):
        glst = [ self.chdir() ]
        flst = [] 
        while glst:
            g = glst.pop()
            flst += g.variables.values()
        if dimopt:
            flst = filter(lambda x: x.dimensions[0] == dimopt, flst)
        if regex:
            if isinstance(regex, basestring):
                regex = re.compile(regex)
            plst = map(lambda x: self.variablePath(x), flst)
            plst = zip(plst,flst)
            plst = filter(lambda x: regex.search(x[0]), plst)
            flst = map(lambda x: x[1], plst)
        return(flst)

    def subsets(self):
        g = self.chdir()
        c = g.groups
        return(c) 

    def _select_flags(self, *flags, **kw):
        if not flags:
            flags = self.flags(**kw)
        vlst = []
        for f in flags:
            if isinstance(f, basestring):
                vlst += self.flags(regex=f)
            else:
                vlst.append(f)
        flags = vlst
        dlst = map(lambda x: x.dimensions[0], flags)
        dlst = {}.fromkeys(dlst)
        if len(dlst.keys()) > 1:
            raise ValueError('different common dimensions for flags: %s', ','.join(dlst.keys()))
        return(flags)
        
    def good(self, *flags, **kw):
        idx = []
        if 'idx' in kw:
            idx = kw['idx']
        flags = self._select_flags(*flags, **kw)
        mask = None
        for f in flags:
            o = self.flag(f)
            if mask is None:
                mask = o.good(idx)
            else:
                mask = np.logical_and(mask, o.good(idx))
        return(mask)
    
    def bad(self, *flags, **kw):
        idx = []
        if 'idx' in kw:
            idx = kw['idx']
        flags = self._select_flags(*flags, **kw)
        mask = None
        for f in flags:
            o = self.flag(f)
            if mask is None:
                mask = o.good(idx)
            else:
                mask = np.logical_or(mask, o.good(idx))
        return(~mask)

  
class Flag(netCDF):

    _FLAGS_GROUP   = None  # Class of group containing this flag, or path to NC group
    _SUBSET_NAME   = None  # GroupName of variable associated to this flag, if any, or NC variable
    _DIMENSIONS    = None
    _DESCRIPTION   = None  
    _VARIABLE_NAME = None  # Class of variable the flag is related to (if any)
      
    def __init__(self, fnc, flag_name=None, **kw):
        super(Flag, self).__init__(fnc)
        opts = {  
                'group'      : self._FLAGS_GROUP, 
                'subset'     : self._SUBSET_NAME, 
                'dimensions' : self._DIMENSIONS,
                'description': self._DESCRIPTION,
                'variable'   : self._VARIABLE_NAME,
                }
        for k in opts.keys():
            if k in kw:
                opts[k] = kw[k]
            a = '_flag_' + k
            setattr(self, a, opts[k])
        self._flag_group = self._flag_group(self._nc)
        if flag_name is None:
            self._flag_name  = self.__class__.__name__.split('.')[-1]
        else:
            self._flag_name = flag_name
        #
        path = [ self._flag_group._group ]
        if self._flag_subset:
            path.append(self._flag_subset)
        self._group = '/'.join(path)
        self.createPath(self._group)
        g = self.chdir()
        if self._flag_name not in g.variables:
            self.create()
        return

    def __getattr__(self, name):
        g  = self.chdir()
        v = g.variables[self._flag_name]
        if name in v.ncattrs():
            return(v.getncattr(name))
        while g is not None:
            if name in g.ncattrs():
                return(g.getncattr(name))
            g = g.parent
        raise(AttributeError, 'no attribute named %s', name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return(object.__setattr__(self, name, value))
        g = self.chdir()
        v = g.variables[self._flag_name]
        if name in v.ncattrs():
            v.setncattr(name, value)
        while g is not None:
            if name in g.ncattrs():
                g.setncattr(name, value)
                return
            g = g.parent
        v.setncattr(name, value)
        return
  
    def __contains__(self, name):
        try:
            self.__getattr__(name)
            return(True)
        except:
            return(False)
        assert False, 'Unreachable code reached'

    def __getitem__(self, idx):
        g = self.chdir()
        v = g.variables[self._flag_name]
        if idx is None:
            return(v)
        return(v[:][idx])
    
    def __setitem__(self, idx, value):
        g = self.chdir()
        v = g.variables[self._flag_name]
        q = v[:]
        q[idx] = value
        v[:] = q
        return
    
    def create(self):
        if self._flag_description is None:
            self._flag_description = 'undocumented flag'
        g = self.chdir()
        if self._flag_name not in g.variables:
            v = self.createVariable(g, self._flag_name, 'none', dtype=np.int8, dims=self._flag_dimensions, fill=-999)
            if not v:
                return
            for k in filter(lambda x: x.startswith('_flag_'), self.__dict__.keys()):
                a = getattr(self, k)
                if isinstance(a, Flags):
                    for q in ('_context_node', '_group_name'):
                        v.setncattr(q, getattr(a, q))
                else:
                    v.setncattr(k, a)
        v = g.variables[self._flag_name]
        v[:] = 0
        return
    
    def good(self, idx=[]):
        mask = (self[:] > 0)
        if np.ma.isMA(self[:]):
            mask &= ~self[:].mask
        if idx:
            mask = mask[idx]
        return(mask)
    
    def bad(self, idx=[]):
        mask = (self[:] < 0)
        if np.ma.isMA(self[:]):
            mask |= self[:].mask
        if idx:
            mask = mask[idx]
        return(mask)

    def setGood(self, idx=[]):
        if len(idx):
            self[idx] = 1
        return
    
    def setBad(self, idx=[]):
        if len(idx):
            self[idx] = -1
        return

    def set(self, good=[], bad=[]):
        self.setGood(good)
        self.setBad(bad)
        return

def getSimVarFlagClasses(ncfile, var_regex, flag_name, subclasses, flag_opts, **kw):
    
    d = { 
         '_FLAGS_GROUP'  : flag_opts['group'],
         '_SUBSET_NAME'  : flag_opts['subset'],
         '_DESCRIPTION'  : flag_opts['description'],
         '_DIMENSIONS'   : flag_opts['dimensions'],
         '_VARIABLE_NAME': flag_opts['variable'],
         }
    if d['_DIMENSIONS'] is None:
        d['_DIMENSIONS'] = ('d_time',) 
    if d['_SUBSET_NAME'] is None:
        d['_SUBSET_NAME'] = '{_var_}'
    if d['_VARIABLE_NAME'] is None:
        d['_VARIABLE_NAME'] = '{_var_}'

    if ('args' not in kw):
        kw['args'] = ()
    if ('opts' not in kw):
        kw['opts'] = {}
    
    fgrp  = d['_FLAGS_GROUP'](ncfile)
    vdict = fgrp.contextNode().variables
    if isinstance(var_regex, basestring):
        var_regex = re.compile(var_regex)
    klst = filter(lambda x: var_regex.search(x), vdict.keys())
    clst = []
    for k in klst:
        oo = dict(map(lambda x: (x,kw[x]), kw['args']))
        oo.update(kw['opts'])
        dd = {}
        dd.update(d)
        oo['_var_'] = k
        dd['_DESCRIPTION']   = dd['_DESCRIPTION'].format(**oo)
        dd['_SUBSET_NAME']   = dd['_SUBSET_NAME'].format(**oo)
        dd['_VARIABLE_NAME'] = dd['_VARIABLE_NAME'].format(**oo)
        dd['_VARIABLE']      = vdict[k]
        fname = flag_name.format(**oo)
        cls = new.classobj(fname.upper(), subclasses, dd)
        clst.append(cls)
    return(clst)

    
        
    
    
    
    

