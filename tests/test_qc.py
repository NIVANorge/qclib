'''
Created on 15. jan. 2018
@author: ELP
'''
import unittest
import pandas as pd
import qclib.QC
from qclib.utils.qc_input import QCInput_df, QCInput, Measurement
from qclib.utils.validate_input import validate_additional_data
import qclib.utils.Thresholds
from qclib import Platforms
from qclib.PlatformQC import PlatformQC
from datetime import datetime, timedelta
from qclib import QC
import qclib.utils.Thresholds as th

platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests

base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)


def make_spiky_data(val_base, val_spike):
    spiky_historical_data = pd.DataFrame.from_dict(
        {"data": [val_base], "time": [base_time - d]})

    spiky_future_data = pd.DataFrame.from_dict({
        "data": [val_base], "time": [base_time + d]})

    spiky_data = QCInput_df(
        current_data=pd.DataFrame.from_dict(
            {"data": [val_spike], "time": base_time}),
        historical_data=spiky_historical_data,
        future_data=spiky_future_data)
    validate_additional_data(spiky_data)
    return spiky_data


def make_frozen_data(len_data):
    frozen_historical_data = pd.DataFrame.from_dict(
        {"data": [12] * len_data,
         "time": [base_time - d * n for n in range(1, len_data + 1)]})

    frozen_data = QCInput_df(current_data=pd.DataFrame.from_dict(
        {"data": [12], "time": base_time}),
        historical_data=frozen_historical_data,
        future_data=None)
    validate_additional_data(frozen_data)
    return frozen_data


def make_complete_data(len_data):
    historical_data = pd.DataFrame.from_dict(
        {"data": [10 + i for i in range(1, len_data)],
         "time": [base_time - d * n for n in range(1, len_data)]})

    future_data = pd.DataFrame.from_dict(
        {"data": [11 + i for i in range(1, len_data)],
         "time": [base_time + d * n for n in range(1, len_data)]})

    data = QCInput_df(current_data=pd.DataFrame.from_dict(
        {"data": [19.5], "time": base_time}), latitude=61, longitude=10.708,
        historical_data=historical_data,
        future_data=future_data)

    validate_additional_data(data)
    return data


def make_complete_input_data(len_data):
    historical_data = [Measurement(value=10 + i, datetime=base_time - d * i) for i in range(1, len_data)]
    future_data = [Measurement(value=10 + i, datetime=base_time + d * i) for i in range(1, len_data)]
    data = QCInput(value=20, timestamp=base_time, latitude=61, longitude=10.708,
                   historical_data=historical_data, future_data=future_data)

    return data


def make_test_data(value):
    return QCInput_df(
        current_data=pd.DataFrame.from_dict(
            {"data": [value], "time": base_time}),
        historical_data=None, future_data=None)


def make_local_test_data(value, lat, long):
    return QCInput_df(
        current_data=pd.DataFrame.from_dict({"data": [value], "time": base_time}),
        longitude=long, latitude=lat,
        historical_data=None, future_data=None)


class Tests(unittest.TestCase):
    final_flag_is_plus_one = {"test1": 1, "test2": 1, "test3": 1, "test4": 1, "test5": 1}
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

    def test_local_range_test(self):
        params_t = {'min': -2.0, 'max': 24.0, 'area': th.Arctic, 'months': th.all_months}
        params_o2 = {'min': 200.0, 'max': 500.0, 'area': th.NorthSea, 'months': th.all_months}
        local_bad_data_t = make_local_test_data(77, 61, 10.708)
        local_good_data_t = make_local_test_data(20, 61, 10.708)
        local_bad_data_o2 = make_local_test_data(77, 59.9, 9)
        flag = common_tests['temperature']['local_range_test'][0](local_bad_data_t, **params_t)
        self.assertEqual(flag, -1, "local_range_test should fail")
        flag = common_tests['temperature']['local_range_test'][0](local_good_data_t, **params_t)
        self.assertEqual(flag, 1)
        flag = common_tests['oxygen_concentration']['local_range_test'][0](local_bad_data_o2, **params_o2)
        self.assertEqual(flag, -1, "local_range_test should fail")

    def argo_spike(self, name, spiky_data):
        measurement_name = name
        params = common_tests[measurement_name]['argo_spike_test'][1]
        flags = common_tests[measurement_name]['argo_spike_test'][0](spiky_data, **params)
        self.assertEqual(flags, -1)

    def test_argo_spike_oxygen(self):
        spiky_data = make_spiky_data(0, 60)
        self.argo_spike('oxygen_concentration', spiky_data)

    def test_argo_spike_temperature(self):
        spiky_data = make_spiky_data(1, 10)
        self.argo_spike('temperature', spiky_data)

    def test_final_flag_logic(self):
        from qclib.PlatformQC import PlatformQC
        flag = PlatformQC.rt_get_overall_flag(self.final_flag_is_plus_one)
        flag_c = PlatformQC.flag2copernicus(flag)
        self.assertEqual(flag, 1)
        self.assertEqual(flag_c, 1)
        flag = PlatformQC.rt_get_overall_flag(self.final_flag_is_minus_one)
        flag_c = PlatformQC.flag2copernicus(flag)
        self.assertEqual(flag, -1)
        self.assertEqual(flag_c, 4)
        flag = PlatformQC.rt_get_overall_flag(self.final_flag_is_zero)
        flag_c = PlatformQC.flag2copernicus(flag)
        self.assertEqual(flag, 0)
        self.assertEqual(flag_c, 0)

    def test_applyQC(self):
        obj = Platforms.FerryboxQC()
        data = make_complete_data(5)
        tests = {"temperature": ["local_range_test", "global_range_test", "argo_spike_test", "frozen_test",
                                 "missing_value_test"]}
        flags = obj.applyQC(data, tests)
        self.assertEqual(PlatformQC.rt_get_overall_flag(flags), 1)

    def test_execute_qc(self):
        obj = Platforms.FerryboxQC()
        data = make_complete_input_data(5)
        tests = {"temperature": ["local_range_test", "global_range_test", "argo_spike_test", "frozen_test",
                                 "missing_value_test"]}
        flags = QC.execute(obj, data, tests)
        self.assertEqual(PlatformQC.rt_get_overall_flag(flags), 1)


if __name__ == '__main__':
    unittest.main()
