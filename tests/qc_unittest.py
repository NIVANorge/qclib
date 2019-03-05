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
from datetime import datetime

global f,now
platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests

f = '%Y-%m-%d %H:%M:%S'
now = datetime.strptime('2017-01-12 14:12:06', f)

def make_spiky_data():
    spiky_historical_data = pd.DataFrame.from_dict(
        {"data": [3],
         "time": [datetime.strptime('2017-01-12 14:08:06', f)]})
    spiky_historical_data = spiky_historical_data.set_index(["time"])

    spiky_future_data = pd.DataFrame.from_dict({
        "data": [3],
        "time": [datetime.strptime('2017-01-12 14:31:06', f)]})
    spiky_future_data = spiky_future_data.set_index(["time"])

    spiky_data = QCInput_df(current_data=pd.DataFrame.from_dict(
                {"data": [20], "time": now}),
                historical_data=spiky_historical_data,
                future_data=spiky_future_data)
    return spiky_data

def make_frozen_data():
    frozen_historical_data = pd.DataFrame.from_dict(
        {"data": [12, 12, 12, 12],
         "time": [datetime.strptime('2017-01-12 14:08:06', f),
                  datetime.strptime('2017-01-12 14:09:06', f),
                  datetime.strptime('2017-01-12 14:10:06', f),
                  datetime.strptime('2017-01-12 14:11:06', f)]})

    frozen_historical_data = frozen_historical_data.set_index(["time"])
    
    frozen_data = QCInput_df(current_data=pd.DataFrame.from_dict(
                    {"data": [12], "time": now}),
                    historical_data=frozen_historical_data,
                    future_data=None)

    return frozen_data                         

class Tests(unittest.TestCase):
    
    missing_data = QCInput_df(current_data=pd.DataFrame.from_dict({"data": [-999], "time": now}),
                              historical_data=None, future_data=None)

    global_bad_salinity_data = QCInput_df(current_data=pd.DataFrame.from_dict({"data": [77], "time": now}),
                                          historical_data=None, future_data=None)

    local_bad_oxygen_concentration_data = QCInput_df(current_data=pd.DataFrame.from_dict({"data": [77], "time": now}),
                                                     longitude=10.7087, latitude=59.9091,
                                                    historical_data=None, future_data=None)
    spiky_data = make_spiky_data()
    frozen_data = make_frozen_data()

    final_flag_is_plus_one = {"test1": 0, "test2": 0, "test3": 1, "test4": 0, "test5": 0}
    final_flag_is_minus_one = {"test1": 0, "test2": 0, "test3": 1, "test4": 0, "test5": -1}
    final_flag_is_zero = {"test1": 0, "test2": 0, "test3": 0, "test4": 0, "test5": 0}

    def test_rt_frozen_test(self):
        # Checks if values are frozen for 5 or more values in a row should give -1 flags for bad data '''
        flag = common_tests['*']['frozen_test'][0](self.frozen_data)
        self.assertEqual(flag, -1)

    def test_missing_value(self):
        # Checks if values are missing with defined value should give -1 flags for bad data
        params = common_tests['*']['missing_value_test'][1]
        flag = common_tests['*']['missing_value_test'][0](self.missing_data, **params)
        self.assertEqual(flag, -1)

    def test_range_global(self):
        # Checks if values are within defined range should give -1 flags for outliers'''
        measurement_name = "salinity"
        params = common_tests[measurement_name]['global_range_test'][1]
        flag = common_tests[measurement_name]['global_range_test'][0](self.global_bad_salinity_data, **params)
        self.assertEqual(flag, -1)

    def test_range_local(self):
        # Checks if values are within defined range for local regions and time periods should give -1 flags for outliers
        measurement_name = 'oxygen_concentration'
        params = common_tests[measurement_name]['local_range_test'][1]
        arr = [[common_tests[measurement_name]['local_range_test'][0], x] for x in params]
        flags= [a[0](self.local_bad_oxygen_concentration_data, **a[1]) for a in arr]

        if all([flg == 0 for flg in flags]):
            combined_flag = 0
        elif any([flg == -1 for flg in flags]):
            combined_flag = -1
        else:
            combined_flag = 1
        self.assertEqual(combined_flag, -1)

    def test_argo_spike(self):
        measurement_name = 'temperature'
        params = common_tests[measurement_name]['argo_spike_test'][1]
        flags = common_tests[measurement_name]['argo_spike_test'][0](self.spiky_data,**params)
        self.assertEqual(flags,-1) 

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