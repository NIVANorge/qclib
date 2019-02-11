'''
Created on 15. jan. 2018
@author: ELP
'''
import unittest
import pandas as pd 
import qclib.QC
from qclib.utils.qc_input import QCInput
from qclib.utils.Thresholds import Global_Threshold_Ranges
import numpy as np
from datetime import datetime


platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests


class Tests(unittest.TestCase):

    now = datetime.strptime('2017-01-12 14:12:06', '%Y-%m-%d %H:%M:%S')

    historical_data = pd.DataFrame.from_dict(
        {"data": [12, 12, 12, 12],
         "time": [datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S'),
                  datetime.strptime('2017-01-12 14:09:06', '%Y-%m-%d %H:%M:%S'),
                  datetime.strptime('2017-01-12 14:10:06', '%Y-%m-%d %H:%M:%S'),
                  datetime.strptime('2017-01-12 14:11:06', '%Y-%m-%d %H:%M:%S')]})
    historical_data = historical_data.set_index(["time"])
    frozen_data = QCInput(value=12, timestamp=now, historical_data=historical_data)
    missing_data = QCInput(value=-999, timestamp=now)
    global_bad_salinity_data = QCInput(value=-77, timestamp=now)
    local_bad_oxygen_concentration_data = QCInput(value=1, timestamp=now, longitude=10.7087, latitude=59.9091)

    final_flag_is_plus_one = [0,0,1,0,0]
    final_flag_is_minus_one = [0, 0, 1, 0, -1]
    final_flag_is_zero = [0, 0, 0, 0, 0]

    def test_rt_frozen_test(self):
        # Checks if values are frozen for 5 or more values in a row should give -1 flags for bad data '''
        flag = common_tests['*']['frozen_test'][0](self.frozen_data)
        self.assertEqual(flag, -1)

    def test_missing_value(self): 
        # Checks if values are missing with defined value should give -1 flags for bad data
        params = common_tests['*']['missing_value_test'][1]
        flag = common_tests['*']['missing_value_test'][0](self.missing_data,**params)
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

        flags = np.zeros([len(arr)])
        for i, a in enumerate(arr):
            flag = a[0](self.local_bad_oxygen_concentration_data, **a[1])
            flags[i] = flag

        if all([flg == 0 for flg in flags]):
            combined_flag = 0
        elif any([flg == -1 for flg in flags]):
            combined_flag = -1
        else:
            combined_flag = 1
        self.assertEqual(combined_flag, -1)

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
