'''
Created on 15. jan. 2018
@author: ELP
'''
import unittest
import pandas as pd
import qclib.QC
from qclib.utils.qc_input import QCInput_df,QCInput
import qclib.utils.Thresholds
import numpy as np
from datetime import datetime,timedelta

platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests

base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)

def make_spiky_data(val_base,val_spike):

    spiky_historical_data = pd.DataFrame.from_dict(
                        {"data": [val_base],"time": [base_time - d]})
    spiky_historical_data = spiky_historical_data.set_index(["time"])

    spiky_future_data = pd.DataFrame.from_dict({
                        "data": [val_base], "time": [base_time + d]})
    spiky_future_data = spiky_future_data.set_index(["time"])

    spiky_data = QCInput_df(
                current_data=pd.DataFrame.from_dict(
                {"data": [val_spike], "time": base_time}),
                historical_data=spiky_historical_data,
                future_data=spiky_future_data)
    return spiky_data

def make_frozen_data(len_data):
    frozen_historical_data = pd.DataFrame.from_dict(
        {"data": [12]*len_data,
         "time": [base_time + d*n for n in range(0,len_data)]})
    frozen_historical_data = frozen_historical_data.set_index(["time"])
    
    frozen_data = QCInput_df(current_data=pd.DataFrame.from_dict(
                    {"data": [12], "time": base_time}),
                    historical_data=frozen_historical_data,
                    future_data=None)
    return frozen_data                         

def make_test_data(value):
    return QCInput_df(
        current_data=pd.DataFrame.from_dict(
        {"data": [value], "time": base_time}),
        historical_data=None, future_data=None)

def make_local_test_data(value,lat,long):
    return QCInput_df(
        current_data=pd.DataFrame.from_dict({"data": [value], "time": base_time}),
        longitude=long, latitude=lat,
        historical_data=None, future_data=None)    

class Tests(unittest.TestCase):
    
    final_flag_is_plus_one = {"test1": 0, "test2": 0, "test3": 1, "test4": 0, "test5": 0}
    final_flag_is_minus_one = {"test1": 0, "test2": 0, "test3": 1, "test4": 0, "test5": -1}
    final_flag_is_zero = {"test1": 0, "test2": 0, "test3": 0, "test4": 0, "test5": 0}

    def test_rt_frozen_test(self):
        # Checks if values are frozen for 5 or more values in a row should give -1 flags for bad data 
        frozen_data = make_frozen_data(4)
        flag = common_tests['*']['frozen_test'][0](frozen_data)
        self.assertEqual(flag, -1)

    def test_missing_value(self):
        # Checks if values are missing with defined value should give -1 flags for bad data
        missing_data = make_test_data(-999)
        params = common_tests['*']['missing_value_test'][1]
        flag = common_tests['*']['missing_value_test'][0](missing_data, **params)
        self.assertEqual(flag, -1)

    def test_range_global(self):
        # Checks if values are within defined range should give -1 flags for outliers
        measurement_name = "salinity"
        global_bad_salinity_data = make_test_data(77)
        params = common_tests[measurement_name]['global_range_test'][1]
        flag = common_tests[measurement_name]['global_range_test'][0](global_bad_salinity_data, **params)
        self.assertEqual(flag, -1)

    def range_local(self,name,data):
        # Checks if values are within defined range for local regions and time periods should give -1 flags for outliers
        measurement_name = name
        params = common_tests[measurement_name]['local_range_test'][1]
        arr = [[common_tests[measurement_name]['local_range_test'][0], x] for x in params]
        flags= [a[0](data, **a[1]) for a in arr]
        if all([flg == 0 for flg in flags]):
            combined_flag = 0
        elif any([flg == -1 for flg in flags]):
            combined_flag = -1
        else:
            combined_flag = 1
        self.assertEqual(combined_flag, -1)

    def test_oxygen_range_local(self):
        #North Sea
        local_bad_data = make_local_test_data(77,59.9,10.708)
        self.range_local('oxygen_concentration', local_bad_data)

    def test_temperature_range_local(self):
        #Arctic 
        local_bad_data = make_local_test_data(77,61,10.708)
        self.range_local('temperature', local_bad_data)

    def argo_spike(self,name,spiky_data):
        measurement_name = name
        params = common_tests[measurement_name]['argo_spike_test'][1]
        flags = common_tests[measurement_name]['argo_spike_test'][0](spiky_data,**params)
        self.assertEqual(flags,-1) 

    def test_argo_spike_oxygen(self):
        spiky_data = make_spiky_data(0,60)
        self.argo_spike('oxygen_concentration', spiky_data) 

    def test_argo_spike_temperature(self):
        spiky_data = make_spiky_data(1,10)
        self.argo_spike('temperature', spiky_data)    

    def test_final_flag_logic(self):
        from qclib.PlatformQC import PlatformQC
        flag = PlatformQC.rt_get_overall_flag(self.final_flag_is_plus_one)
        self.assertEqual(flag, 1)
        flag = PlatformQC.rt_get_overall_flag(self.final_flag_is_minus_one)
        self.assertEqual(flag, -1)
        flag = PlatformQC.rt_get_overall_flag(self.final_flag_is_zero)
        self.assertEqual(flag, 0)


if __name__ == '__main__':
    unittest.main()