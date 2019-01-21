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
import itertools

# '''
# In the document 
# http://archimer.ifremer.fr/doc/00251/36232/
# the ranges are defined for different depths 
# For now the ranges defined here only for the surface
# '''
common_tests = {

     '*':
         { 'FROZEN_TEST': [QCTests.RT_frozen_test,{}],
           'MISSING_VALUE': [QCTests.missing_value_test,{'nan':-999}
                             ]},
     'temperature':
         { 'GLOBAL_RANGE': [QCTests.range_test, 
                            Thresholds.Global_Threshold_Ranges.Temperature]},
     'salinity':
         { 'GLOBAL_RANGE': [QCTests.range_test, 
                            Thresholds.Global_Threshold_Ranges.Salinity]},
     'fluorescence':
         { 'GLOBAL_RANGE': [QCTests.range_test, 
                            Thresholds.Global_Threshold_Ranges.Fluorescence],
           'LOCAL_RANGE' : [QCTests.range_test, 
                            Thresholds.Local_Threshold_Ranges.Fluorescence]},
     'oxygen_concentration':
         { 'GLOBAL_RANGE': [QCTests.range_test, 
                            Thresholds.Global_Threshold_Ranges.Oxygen],
           'LOCAL_RANGE' : [QCTests.range_test, 
                            Thresholds.Local_Threshold_Ranges.Oxygen]}}
                            
class PlatformQC(QCTests):

    sampling_frequency = 60
    frequency_units = "seconds"

    def __init__(self):
        self.qc_tests = common_tests.copy()

    def applyQC(self, df, tests):

        """
      df : dataframe wih col: datetime, name (platform code), lon, lat, data
         where data is e.g. salinity or temperature, or fdom, etc.,..
     tests : dictionary with key being name (e.g. temperature, or salinity, or...)
      and with value being a list of tests =["global_range","local_range"]...
        """

        flags={}
        key = list(tests.keys())[0]
        if key in ['temperature','oxygen_concentration','fluorescence','salinity']:
            self.qc_tests[key].update(self.qc_tests['*'])

        # uncomment to use tests from metadata
        for test in tests[key]:
#        for test in self.qc_tests[key]:
# TODO check why below was commented out
            #ns = self.qc_tests[key][test][0].size
            #df = df[0:ns]
            if key not in self.qc_tests:
                key = "*"

            if type(self.qc_tests[key][test][1]) is list:
                # ONLY LOCAL_RANGE TEST 
                arr = [[test,self.qc_tests[key][test][0], x] for x in self.qc_tests[key][test][1]]

                for n,a in enumerate(arr):
                    flag = a[1](df, **a[2])
                    if test not in flags:
                        flags[test] = np.zeros([len(arr),len(df.data)])
                        flags[test][n] = flag 
                    else:
                        flags[test][n] = flag                       
               
                combined_flags = []
                for f in flags[test].T:
                    if (f == -1).sum() > 0:
                        combined_flags.append(-1)
                    elif all([ff == 0 for ff in f]):
                        combined_flags.append(0)
                    else: 
                        combined_flags.append(1)                
                flags[test] =  combined_flags
                #print ('after' ,flags[test])
    
            else:
                print(df)
                flag = self.qc_tests[key][test][0](df, **self.qc_tests[key][test][1])
                if test not in flags:
                    flags[test] = flag
            
        return flags

    # FIXME: ask Liza and Pierre about CMEMScodes function (needed?) 
    # and local_range (does format_flags do what it should...?)
    '''def format_flags(self,flags):

        for k,v in flags.items():
            if type(v) is list:
                if v.count(-1)>0:
                    flags[k]=-1
                elif  all([v == 0 for v in flags ]):
                    flags[k]=0
                else:
                    flags[k]=1'''
                    
                    
    @classmethod
    def derive_overall_flag(cls,flags, system_flags):
        #print ('derive_overall_flag',flags)
        derived_flags = [v for k,v in flags.items()]
        n_meas = len(derived_flags[0])
        
        flgs = list(itertools.chain.from_iterable(derived_flags))        

        if n_meas == 1 and len(flgs) > 1 : 
            if all([ff == -1 for ff in flgs]):
                overall_flags= -1
            elif all([ff == 0 for ff in flgs]):
                overall_flags= 0 
            else: 
                overall_flags= 1    
            #print ('one meas, many tests',overall_flags) 
        elif (n_meas == 1 and len(flgs) == 1) : 
            overall_flags = flgs
            #print ('only one', flgs)            
        else:
            overall_flags = []
            # This loop does not take into accout 
            # levels and system flags 
            for f in np.array(derived_flags).T :
                if all([ff == -1 for ff in f]):
                    overall_flags.append(-1)
                elif all([ff == 0 for ff in f]):
                    overall_flags.append(0)
                else: 
                    overall_flags.append(1)
            #print ('long case ',n_meas,overall_flags)

        return overall_flags

    @classmethod
    def overall_derived_flag(cls, flags):
        # print ('derive_overall_flag',flags)

        if all([flg == 0 for flg in flags]):
            return 0

        for flg in flags:
            if flg == -1:
                return -1

        overall_flag = 1
        return overall_flag

    @classmethod
    def CMEMScodes(cls, flags):
    # FIXME This function will not work with the new interface, 
    # since flags do not have the top level key being measurement name.
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
