'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Platforms.Common
========================
Common classes and tools for platforms

Created on 14. feb. 2018
'''

import sys
import json
import datetime

import numpy as np
#from ..QC import QCTests, COMMON_TESTS
#ValueError: attempted relative import beyond top-level package
from pyFerry.Globals import Areas
from pyFerry.QC import QCTests, COMMON_TESTS
import code


class PlatformQC(QCTests):
    
    QC_TESTS = 'to be subclassed'
       
    @classmethod                 
    def applyQC(cls, meta, data):
        """
        Apply QC for all registered parameters
        
        Each platform should sublass this class and define its own list of tests in class variable `QC_TESTS`.
        
        QC definitions are found in the common list `COMMON_TESTS` and in the platform specific class variable 
        `QC_TESTS`. 
        
        Argument `meta` is a dictionary with keys required by the specific QC tests, as well as
        
          *sensor_list*  : list of all lowest level sensors in the platform
          *<sensor_name>*: a dictionary for each lowest level sensor sensor with key `parameter_type` defining 
                           the type of parameter being measured.
                         
        Argument `data` is a dictionary with the data for each lowest level sensor.

        The return value is a dictionary of flags where keys are sensor names containing dictonaries of
        test results. 
        
        Example:
        --------
        
          meta = { 
            'signal_list': [ 'CTD_TEMPERATURE', 'CTD_SALINITY', 'O2T', ... ],
            'CTD_TEMPERATURE': { 'parameter_type': 'TEMPERATURE' },
            'CTD_SALINITY'   : { 'parameter_type': 'SALINITY' },
            'O2T': { 'parameter_type': 'TEMPERATURE' },
            }
          data = {
            'CTD_TEMPERATURE': np.array([ ... ]),
            'CTD_SALINITY'   : np.array([ ... ]),
            'O2T'            : np.array([ ... ]),
            }
        
          flags = {
            'CTD_TEMPERATURE': {
              'FROZEN_VALUE': np.array([ ... ]),
              'GLOBAL_RANGE': np.array([ ... ]),
              ...
              },
            'CTD_SALINITY': {
              'FROZEN_VALUE': np.array([ ... ]),
              'GLOBAL_RANGE': np.array([ ... ]),
              ...
              },
            ...
            }
            
        """
        flags  = {}
        # Concatenate lists of QC_TESTS 
        qclist = {}        
        qclist.update(COMMON_TESTS)
        for k in cls.QC_TESTS.keys():
            if k not in qclist:
                qclist[k] = cls.QC_TESTS[k]
            else:
                qclist[k].append(cls.QC_TESTS[k])
            
        # Apply QC for each parameter
        signal_list = meta['signal_list']
        for signal_k in signal_list:
            signal_d = data[signal_k]
            if signal_k not in flags:
                flags[signal_k] = {}

            param_t = meta[signal_k]['parameter_type']

            # For code simplicity, build a list of all QC for that parameter
            qcl = []
            if '*' in qclist:
                qcl += qclist['*']
            if param_t in qclist:
                qcl += qclist[param_t]
            # Apply each QC
            for qcdef in qcl:
                flag_d = qcdef[1](meta, signal_d, **qcdef[2])
                flag_k = qcdef[0].upper()
                flags[signal_k][flag_k] = flag_d.tolist()
                
        return(flags)
        
          
            
    @classmethod
    def CMEMScodes(cls, flags):
        """
        Convert the given flags to the standards CMEMS flag codes
        
        Argument flags is expected to be in the same format as the result from method `applyQC`.
        
        Return value is a dict where signal names har mapped to the array of CMEMS QC codes.
        """
        codes = {}
        overall_flags = {}
        for signal_k in flags.keys():
            flst = list(flags[signal_k].keys())
            if not flst:
                continue
            nmax   = len(flags[signal_k][flst[0]])
            code   = np.concatenate(list(flags[signal_k].values()), axis=0)
            code   = np.reshape(code, [len(flst),nmax])

            mask_1 = np.any(code == -1, axis= 0) 
            mask_0 = np.all(code == 0, axis= 0)
            code = np.ones(code.shape[1], dtype=np.int8)
            overall_flag = code.copy()
            overall_flag[mask_1]= -1 
            overall_flag[mask_0] = 0            
            code[mask_1] = 4
            code[mask_0] = 0
            codes[signal_k] = code.tolist()
            overall_flags[signal_k] = overall_flag.tolist()
        return(codes,overall_flags)
            
    @classmethod 
    def FlagOverall(cls,codes,flags):
        for code in codes:
            mask = np.any(code == 4)
            code[mask] = -1 
            
                    
    @classmethod
    def clusterizeFlags(cls, d):
        """
        Modifies a nested dictionary ending with numpy arrays into a list of clusters, one for each 
        element in the arrays. Each cluster is a nested dictionary of the same structure as the input
        by it ends with the element values of each item. 
        
        You should expect that all inputn arrays have the same length.
        """
        lst = []
        for k in d.keys():
            if isinstance(d[k], dict):
                l = cls.clusterizeFlags(d[k])
                if len(lst):
                    map(lambda x: lst[x].update({k:l[x]}), range(len(l)))
                else:
                    lst = map(lambda x: {k:x}, l)
            else:
                if len(lst):
                    map(lambda x: lst[x].update({k:d[k][x]}), range(len(d[k])))
                else:
                    lst = map(lambda x: {k:d[k][x]}, range(len(d[k]))) 
        return(lst)
    
            
    @classmethod
    def JSONformat(cls, name, flags, time): 
        """
        Generate JSON format for QC flags. Time is added for each element in order to know where
        they belong to. Calling with the UUID of the measurement set would be more safe.
        """
        lst = cls.clusterizeFlags(flags)
        lst = map(lambda x: { name: x }, lst)
        if not isinstance(time[0], basestring):
            t = map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'), time[:])
        map(lambda x: lst[x].update({'time': t[x]}), range(len(time)))
        d = { 't': lst }
        s = json.dumps(d)
        return(s)
    

#
# Testing here
# 
if __name__ == '__main__':
    
    # Testing JSON flags conversion
    t0 = datetime.datetime.now()
    dt = datetime.timedelta(days=1)
    t  = np.array([t0, t0+dt, t0+2*dt, t0+3*dt])
    f  = { 
        'CTD_T': { 'GR': [ 1, 2, 3, 4], 'LR': [ 10, 20, 30, 40] },
        'CTD_S': { 'GR': [ -1, -2, -3, -4], 'LR': [ -10, -20, -30, -40] },
        }
    #s = PlatformQC.clusterizeFlags(f)
    s = PlatformQC.JSONformat('flag_name', f, t)
    pass

          
    
