'''
Created on 15. jan. 2018
@author: ELP
Temporary module for testing 
to be deleted later

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



f = '%Y-%m-%d %H:%M:%S'
now = datetime.strptime('2017-01-12 14:12:06', f)

frozen_historical_data = pd.DataFrame.from_dict(
    {"data": [12, 12, 12, 12],
     "time": [datetime.strptime('2017-01-12 14:08:06', f),
              datetime.strptime('2017-01-12 14:09:06', f),
              datetime.strptime('2017-01-12 14:10:06', f),
              datetime.strptime('2017-01-12 14:11:06', f)]})

spiky_historical_data = pd.DataFrame.from_dict(
    {"data": [3, 20],
     "time": [datetime.strptime('2017-01-12 14:08:06', f),
              datetime.strptime('2017-01-12 14:11:06', f)]})



frozen_historical_data = frozen_historical_data.set_index(["time"])
spiky_historical_data = spiky_historical_data.set_index(["time"])

frozen_data = QCInput(value=12, timestamp=now, historical_data = frozen_historical_data)
spiky_data = QCInput(value=2, timestamp=now, historical_data = spiky_historical_data)

missing_data = QCInput(value=-999, timestamp=now)
global_bad_salinity_data = QCInput(value=-77, timestamp=now)
local_bad_oxygen_concentration_data = QCInput(value=1, timestamp=now, longitude=10.7087, latitude=59.9091)

final_flag_is_plus_one = [0,0,1,0,0]
final_flag_is_minus_one = [0, 0, 1, 0, -1]
final_flag_is_zero = [0, 0, 0, 0, 0]


def test_argo_spike():
    measurement_name = 'temperature'
    params = common_tests[measurement_name]['argo_spike_test'][1]
    flag = common_tests[measurement_name]['argo_spike_test'][0](spiky_data,**params)
    print (flag)
    #[0](self.global_bad_salinity_data, **params)
    #flags = common_tests['*']['argo_spike_test'][0](self.frozen_data)

test_argo_spike()