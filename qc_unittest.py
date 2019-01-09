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


signal_meta = {"time" : datetime.datetime.now(),"name":'TF',"lon":45,"lat":45}

parameter_types = {'CTD_SALINITY' : 'salinity' }


class Tests(unittest.TestCase):
    good = {
       'CHLA_FLUORESCENCE' : [0.345, 10.0, 50,50,148],
       'CTD_SALINITY' :      [ 25.700, 25.720, 77 , 77, 145],
       'CTD_TEMPERATURE' :   [14.024, 14.014, -20, -20,500],
       'GPS_LATITUDE' :      [59.9091, 59.9091, 59.9091, 159.9091,45],
       'GPS_LONGITUDE' :     [10.7057, 10.7077, 10.7087, 70.7087,45],
       'SHIP_CODE' :         ['FA','FA','FA','FA','FA']
        }
         
    df_a = pd.DataFrame(data=good)
    
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
    
    def test_range(self):
        #meas_name = 'CTD_SALINITY'
        #param_type = parameter_types[meas_name]        
        #tests_dict = {}
        #tests_dict[meas_name] = common_tests[param_type]    
        pass
   

            
if __name__ == '__main__':
    unittest.main()