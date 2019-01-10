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
        
    now =  '2017-01-12T14:12:06'    
    signal_meta = {
         "time" : [now,now,now,now,now],
         "name":  ['TF','TF','TF','TF','TF'],
         "lat": [55,55,55,55,55], 
         "lon": [5,5,5,5,5]}    
        
         
    #df_a = pd.DataFrame(data=good_df)
    
    good = np.ones(5, dtype=np.int8)
    bad = [-1,-1,-1,-1,-1]
    
    def test_frozen(self):

        df_frozen = pd.DataFrame()
        df_frozen['data'] = [25.700, 25.700, 25.700, 25.700, 25.700]
        flags = common_tests['*']['FROZEN_TEST'][0](df_frozen)

        self.assertEqual(list(flags),self.bad)

    def test_missing_value(self): 
               
        df_missing = pd.DataFrame()
        df_missing['data'] = [ -999,  -999,  -999,  -999, -999]
        params = common_tests['*']['MISSING_VALUE'][1]
        flags = common_tests['*']['MISSING_VALUE'][0](df_missing,**params)
        
        self.assertEqual(list(flags),self.bad)     
    
    def test_range_global(self):
        df = pd.DataFrame(data = self.signal_meta)
        
        meas_name = 'salinity'
        df['data'] = self.bad_df[meas_name]
        params = common_tests[meas_name]['GLOBAL_RANGE'][1]

        flags = common_tests[meas_name]['GLOBAL_RANGE'][0](df,**params)   

        self.assertEqual(list(flags),self.bad)
        
    def test_range_local(self):
        df = pd.DataFrame(data = self.signal_meta)
        
        meas_name = 'oxygen_concentration'
        df['data'] = self.bad_df[meas_name]        
        params = common_tests[meas_name]['LOCAL_RANGE'][1]        
        arr = [[common_tests[meas_name]['LOCAL_RANGE'][0], x] for x in params]

        flags = []
        for a in arr:
            #print (a[0],'-',a[1])
            flag = a[0](df, **a[1])
            flags.append(flag.tolist())

        # format_flag       
        print(flags,flags.count(-1))
        if flags.count(-1)>0:
            flags=-1
        elif all([f == 0 for f in flags]):
            flags = 0 
        else: 
            flags = 1  
                        
        print (flags)

        #flags = common_tests[meas_name]['LOCAL_RANGE'][0](df,**params)   
        #print (flags)
        #self.assertEqual(list(flags),self.bad)
    

            
if __name__ == '__main__':
    unittest.main()
    
    