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
from QCTests import QCTests
import Thresholds


common_tests = {

     '''
     In the document 
     http://archimer.ifremer.fr/doc/00251/36232/
     the ranges are defined for different depths 
     For now the ranges defined here only for the surface
     '''
 
     '*':
         { 'FROZEN_VALUE': [QCTests.RT_frozen_test,{}], 'MISSING_VALUE': [QCTests.missing_value_test,] },
     'temperature':
         { 'GLOBAL_RANGE': [QCTests.range_test, Thresholds.Global_Threshold_Ranges.Temperature] },
     'salinity':
         { 'GLOBAL_RANGE': [QCTests.range_test, Thresholds.Global_Threshold_Ranges.Salinity] },
     'fluorescence':
         { 'GLOBAL_RANGE': [QCTests.range_test, Thresholds.Global_Threshold_Ranges.Fluorescence],'LOCAL_RANGE': [QCTests.range_test, Thresholds.Local_Threshold_Ranges.Fluorescence] },
     'oxygen_concentration':
         { 'GLOBAL_RANGE': [QCTests.range_test, Thresholds.Global_Threshold_Ranges.Oxygen], 'LOCAL_RANGE': [QCTests.range_test, Thresholds.Local_Threshold_Ranges.Oxygen] }
    }


class PlatformQC(QCTests):

    sampling_frequency = 60
    frequency_units = "seconds"

    def __init__(self):
        self.qc_tests = common_tests.copy()

    def applyQC(self, df, tests):

        """
      df : dataframe wih col: datetime, name (platform code), lon, lat, data
         where data is e.g. salinity or temperature, or fdom, etc.,..
     tests : dictionary with key being name (e.g. temperature, or salinity, or...) and with value being a list of tests =["global_range","local_range"]...
        """

        flags={}
        key = list(tests.keys())[0]
#        for test in tests[key]:
        for test in self.qc_tests[key]:
            ns = self.qc_tests[key][test][0].size
            df = df[0:ns]
            if type(self.qc_tests[key][test][1]) is list:
                arr = [[test,self.qc_tests[key][test][0], x] for x in self.qc_tests[key][test][1]]
                for a in arr:
                    flag = a[1](df, **a[2])
                    if test not in flags:
                        flags[test] = flag.tolist()
                    else:
                        flags[test].append(flag[0])
            else:
                flag = self.qc_tests[key][test][0](df, **self.qc_tests[key][test][1])
                if test not in flags:
                    flags[test] = flag[0]

        return flags

# FIXME: ask Liza and Pierre about CMEMScodes function (needed?) and local_range (does format_flags do what it should...?)
    def format_flags(self,flags):

        for k,v in flags.items():
            if type(v) is list:
                if v.count(-1)>0:
                    flags[k]=-1
                elif  all([v == 0 for v in flags ]):
                    flags[k]=0
                else:
                    flags[k]=1
    @classmethod
    def derive_overall_flag(cls,flags, system_flags):

        derived_flags = [v for k,v in flags.items()]
        flag = -1 if system_flags.count(-1) > 0 or derived_flags.count(-1) > 0 else 1
        if all([v == 0 for v in derived_flags]):
            flag = 0
        return flag

    @classmethod
    def CMEMScodes(cls, flags):
# FIXME This function will not work with the new interface, since flags do not have the top level key being measurement name.
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

          
    
