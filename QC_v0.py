"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Operations.QC
===========================



(C) 18. okt. 2016 Pierre Jaccard
"""
import datetime

import numpy as np

from .netCDF import Generic

from . import Loggers

log = Loggers.getLogger(__name__)

def QCTestDecorator(method):
    def wrapped(flag, var, *args, **kw):
        bad = method(flag, var, *args)
        if ('return_bad' in kw) and kw['return_bad']:
            return(bad)
        flag.set_flags(var, bad)
        return(bad)
    return(wrapped)
        
    
class QCTests(Generic.Flag):

    def set_flags(self, var, bad):
        if np.ma.isMA(bad):
            bad  = np.logical_or(bad, var[:].mask)
        self.set(good=~bad, bad=bad)
        return
    
    @QCTestDecorator
    def frozen_test(self, var, **kw):
        try:
            bad = (np.diff(var[:]) == 0.0)
            bad = np.concatenate((bad[0:1], bad))
        except Exception as err:
            log.error('performing QC test', test='frozen_test', variable=var.name)
            raise(err)
        return(bad)

    @QCTestDecorator
    def range_test(self, var, vmin, vmax, **kw):
        data = var[:]
        bad  = np.zeros(len(data), dtype=np.bool)
        if vmin is not None:
            bad |= (data < vmin)
        if vmax is not None:
            bad |= (data > vmax)
        return(bad)

    @QCTestDecorator
    def history_test(self, var, vmin, vmax, tvar, dtmin, **kw):
        dt   = dtmin/86400.0
        bad  = self.range_test(var, vmin, vmax, return_bad = True)
        idp  = np.zeros(np.shape(bad), dtype=np.int8)
        idp[~bad] = 1 
        idp  = np.where(np.diff(idp) == 1)[0]
        idp += 1
        tdp  = tvar[idp] + dt
        for i in range(len(idp)):
            j = idp[i] 
            m = np.where(tvar[:] > tdp[i])[0]
            if not len(m):
                k = len(bad) - 1
            else:
                k = np.min(m)
            bad[j:k] = True
        return(bad)


class MultiVarQCTests(object):
    
    def __init__(self, ncfile, var_regex, flag_group, **kw):
        self.file             = ncfile
        self.var_regex        = var_regex
        self.flag_group       = flag_group
        self.subclasses       = (QCTests,)
        self.flag_name        = None
        self.flag_description = None
        self.flag_dimensions  = None
        self.flag_subset      = None
        self.flag_variable    = None
        self.update(kw)
        return
      
    def update(self, kw):
        for k in kw.keys():
            if hasattr(self, k):
                setattr(self, k, kw[k])
                del kw[k]
        return
    
    def flag_options(self):
        d = {
             'group'      : self.flag_group,
             'subset'     : self.flag_subset,
             'description': self.flag_description,
             'dimensions' : self.flag_dimensions,
             'variable'   : self.flag_variable,
             }
        return(d)
        
    def frozen_test(self, **kw):
        nc = Generic.netCDF(self.file)
        self.flag_name        = '{_var_}_FROZEN_TEST'
        self.flag_description = 'Applies frozen value test on {_var_}'
        self.update(kw)
        flag_opts = self.flag_options()
        clst = Generic.getSimVarFlagClasses(nc, self.var_regex, self.flag_name, self.subclasses, flag_opts, **kw)
        bad = None
        for cls in clst:
            flag = cls(nc)
            bad  = flag.frozen_test(cls._VARIABLE)
        return(bad)

    def range_test(self, vmin, vmax, **kw):
        nc = Generic.netCDF(self.file)
        args = ('vmin', 'vmax')
        opts = { 'vmin': vmin, 'vmax': vmax, 'args': args }
        self.flag_name   = '{_var_}_RANGE_TEST'
        self.description = 'Applies range value test on {_var_} for [{vmin:<.2f},{vmax:<.2f}]'
        self.update(kw)
        flag_opts = self.flag_options()
        clst = Generic.getSimVarFlagClasses(nc, self.var_regex, self.flag_name, self.subclasses, flag_opts, **kw)
        for cls in clst:
            flag = cls(nc)
            bad  = flag.range_test(cls._VARIABLE, vmin, vmax)
        return
 

    
    
    