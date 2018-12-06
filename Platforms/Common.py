'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Platforms.Common
========================
Common classes and tools for platforms

Created on 14. feb. 2018
'''

import json
import datetime

import numpy as np
from pyFerry.QC import QCTests
from pyFerry import QC
COMMON_TESTS = QC.Properties.common_tests



class PlatformQC(QCTests):
    
    QC_TESTS = 'to be subclassed'
       
    @classmethod                 
    def applyQC(cls, df, tests):

        """
    df : dataframe wih col: datetime, lon, lat, measurement_value
         where measurement is e.g. salinity or temperature, or fdom, etc.,..
     tests : dictionary with key being name (e.g. temperature, or salinity, or...) and with value being a list of tests =["global_range","local_range"]...
        """
# FIXME
        """ somewhere in the code concatenation of common tests with specific platform tests needs to happen
    Currently common_tests are imported from QC and match to the metadata during ingest (rtjson_ingest) so tests contain only common tests which have respective metadata info
    For now it is not a problem because none of the platforms have additional tests
        """
        flags=[]
        key = list(tests.keys())[0]
# Build a list of all QC tests
        for test in tests[key]:
            for qcdef in COMMON_TESTS[key]:
                if test == qcdef[0]:
                    flag =-9999
                    if type(qcdef[2]) is list:
                        name = qcdef[0]
                        test = qcdef[1]
                        arr = [[name, test, x] for x in qcdef[2]]
                        for a in arr:
                            flag = a[1](df, **a[2])
                            flags.append(flag)
                    else:
                        flag = qcdef[1](df, **qcdef[2])
                    flags.append(flag)
        return flags


            
    @classmethod
    def CMEMScodes(cls, flags):
        """
        Convert the given flags to the standards CMEMS flag codes
        Argument flags is expected to be in the same format 
        as the result from method `applyQC`.        
        Return value is a dict where signal names 
        has mapped to the array of CMEMS QC codes.
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
    


# Testing here
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

          
    
