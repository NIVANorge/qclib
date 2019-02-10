'''
Created on 15. jan. 2018
@author: ELP
'''
import unittest
import pandas as pd 
import Thresholds
from QCTests import QCTests
#from PlatformQC import PlatformQC
import datetime
import numpy as np
platform_code = 'TF'

common_tests = {

     '*':
         { 'FROZEN_TEST': [QCTests.rt_frozen_test,{}],
           'MISSING_VALUE': [QCTests.rt_missing_value_test,{'nan':-999}
                             ]},
     'temperature':
         { 'GLOBAL_RANGE': [QCTests.rt_range_test,
                            Thresholds.Global_Threshold_Ranges.Temperature]},
     'salinity':
         { 'GLOBAL_RANGE': [QCTests.rt_range_test,
                            Thresholds.Global_Threshold_Ranges.Salinity]},
     'fluorescence':
         { 'GLOBAL_RANGE': [QCTests.rt_range_test,
                            Thresholds.Global_Threshold_Ranges.Fluorescence],
           'LOCAL_RANGE' : [QCTests.rt_range_test,
                            Thresholds.Local_Threshold_Ranges.Fluorescence]},
     'oxygen_concentration':
         { 'GLOBAL_RANGE': [QCTests.rt_range_test,
                            Thresholds.Global_Threshold_Ranges.Oxygen],
           'LOCAL_RANGE' : [QCTests.rt_range_test,
                            Thresholds.Local_Threshold_Ranges.Oxygen]}}

parameter_types = {'CTD_SALINITY' : 'salinity' }


class Tests(unittest.TestCase):
    bad_df = {
       'CHLA_FLUORESCENCE' : [0.345, 10.0, 50,50,148],
       'salinity' :      [ 250.700, 250.720, -77 , -77, 145],
       'CTD_TEMPERATURE' :   [14.024, 14.014, -20, -20,500],
       'GPS_LATITUDE' :      [59.9091, 59.9091, 59.9091, 159.9091,45],
       'GPS_LONGITUDE' :     [10.7057, 10.7077, 10.7087, 70.7087,45],
       'oxygen_concentration' : [1,1,1,1,1],
       'SHIP_CODE' :         ['FA','FA','FA','FA','FA']
        }
        
    now =  '2017-01-12 14:12:06'
    signal_meta = {
         "time" : [now,now,now,now,now],
         "name":  ['TF','TF','TF','TF','TF'],
         "lat": [55,55,55,55,55], 
         "lon": [5,5,5,5,5]}    
        
    df = pd.DataFrame(data = signal_meta)     

    # all tests should fail with this list of flags 
    #good = np.ones(5, dtype=np.int8)
    
    # flags to check tests 
    bad = [-1,-1,-1,-1,-1]
   
    def test_frozen(self):
        ''' Checks if values are frozen for 5 or more values in a row 
            should give -1 flags for bad data '''
        df_frozen = pd.DataFrame()
        df_frozen['data'] = [25.700, 25.700, 25.700, 25.700, 25.700]
        flags = common_tests['*']['FROZEN_TEST'][0](df_frozen)

        self.assertEqual(list(flags),self.bad)

    def test_missing_value(self): 
        ''' Checks if values are missing with defined value 
            should give -1 flags for bad data '''               
        df_missing = pd.DataFrame()
        df_missing['data'] = [ -999,  -999,  -999,  -999, -999]
        params = common_tests['*']['MISSING_VALUE'][1]
        flags = common_tests['*']['MISSING_VALUE'][0](df_missing,**params)
        
        self.assertEqual(list(flags),self.bad)     
    
    def test_range_global(self):
        ''' Checks if values are within defined range 
            should give -1 flags for outliers'''            
        meas_name = 'salinity'
        self.df['data'] = self.bad_df[meas_name]
        params = common_tests[meas_name]['GLOBAL_RANGE'][1]

        flags = common_tests[meas_name]['GLOBAL_RANGE'][0](self.df,**params)   

        self.assertEqual(list(flags),self.bad)
        
    def test_range_local(self):
        ''' Checks if values are within defined range 
            for local regions and time periods
            should give -1 flags for outliers'''       
        meas_name = 'oxygen_concentration'
        self.df['data'] = self.bad_df[meas_name]        
        params = common_tests[meas_name]['LOCAL_RANGE'][1]        
        arr = [[common_tests[meas_name]['LOCAL_RANGE'][0], x] for x in params]

        flags = np.zeros([len(arr),len(self.df.data)])
        for n,a in enumerate(arr):
            flag = a[0](self.df, **a[1])
            flags[n] = flag
        flags = flags.T

        combined_flags = []
        for f in flags:
            if (f == -1).sum() > 0:
                combined_flags.append(-1)
            elif all([ff == 0 for ff in f]):
                combined_flags.append(0)
            else: 
                combined_flags.append(1)
                
        self.assertEqual(combined_flags,self.bad)                                 
    
            
if __name__ == '__main__':
    unittest.main()
    
    