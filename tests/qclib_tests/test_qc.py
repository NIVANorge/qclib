import csv
import os
import time
import unittest
from datetime import datetime, timedelta
import pytest

import qclib.utils.Thresholds
import qclib.QC as QC
from qclib.utils.qc_input import QCInput
from qclib.PlatformQC import PlatformQC
from qclib.QCTests import QCTests

ORIGIN_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata")
platform_code = 'TF'
common_tests = QC.init(platform_code).qc_tests
base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)


def make_toy_data(size):
    values = [(base_time + d * i, i) for i in range(0, size)]
    location = [(base_time + d * i, 10.708 + i * 0.01, 61 + i * 0.01) for i in range(0, size)]
    return QCInput(values=values, locations=location)


def read_testdata(filename):
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        return list(csv_reader)[1:]


def write_testdata(filename, header, data):
    with open(filename, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        csv_writer.writerow(header)
        csv_writer.writerows(data)


def make_toy_data_with_nan(size):
    values = [(base_time + d * i, i) for i in range(1, size)]
    values.insert(2, (base_time + d * 3, None))
    location = [(base_time + d * i, 10.708 + i * 0.01, 61 + i * 0.01) for i in range(0, size)]
    return QCInput(values=values, locations=location)


class Tests(unittest.TestCase):

    def test_qc_logic(self):
        filename = os.path.join(ORIGIN_DIR, "ferrybox_data.csv")
        input_data = read_testdata(filename)

        values = [(datetime.strptime(item[0].split('.')[0], '%Y-%m-%dT%H:%M:%S'), float(item[1])) for item in
                  input_data]
        locations = [(datetime.strptime(item[0].split('.')[0], '%Y-%m-%dT%H:%M:%S'), float(item[5]), float(item[6]))
                     for item in input_data]

        ref_frozen_test = [int(item[2]) for item in input_data]
        ref_global_range_test = [int(item[3]) for item in input_data]
        ref_argo_spike_test = [int(item[4]) for item in input_data]
        ref_local_range_test = [int(item[7]) for item in input_data]
        ref_final_flag = [int(item[8]) for item in input_data]
        flags = QC.execute(qclib.QC.init(platform_code), QCInput(values=values, locations=locations),
                           measurement_name="salinity",
                           tests=["global_range_test", "frozen_test", "argo_spike_test", "local_range_test"])

        pump_flag = [1] * len(values)
        pump_flag[0] = -1
        pump_flag[49] = -1
        final_flag = PlatformQC.get_overall_flag(flags, pump_flag)

        assert flags["frozen_test"] == ref_frozen_test, "Frozen test failed"
        assert flags["global_range_test"] == ref_global_range_test, "Global range test failed"
        assert flags["argo_spike_test"] == ref_argo_spike_test, "Argo spike test failed"
        assert flags["local_range_test"] == ref_local_range_test, "Local range test failed"
        assert final_flag == ref_final_flag, "Final flag calculation failed"

    def test_warning_on_undefined_qc_test(self):
        with pytest.raises(Exception):
            QC.execute(qclib.QC.init(platform_code), QCInput(values=[(datetime(2018, 1, 1), 1)], locations=None),
                       measurement_name="salinity", tests=['non_existing_test'])

    def test_large_variance_test(self):
        time_stamp = datetime(2018, 4, 10, 17, 45)

        values = [(time_stamp + timedelta(seconds=i), i) for i in range(0, 15)]
        flags = QCTests.bounded_variance_test(QCInput(values=values, locations=None), .6)
        assert flags == [0 if i < 3 else -1 for i in range(0, 15)]

        values = [(time_stamp + timedelta(seconds=i), 1) for i in range(0, 15)]
        flags = QCTests.bounded_variance_test(QCInput(values=values, locations=None), .6)
        assert flags == [0 if i < 3 else 1 for i in range(0, 15)]

    def test_execution_time_with_toy_data(self):
        data = make_toy_data(1500)
        tests = ["local_range_test", "global_range_test", "argo_spike_test", "frozen_test"]
        start = time.time()
        QC.execute(platform=qclib.QC.init(platform_code), qc_input=data, measurement_name="temperature", tests=tests)
        end = time.time()
        assert (end - start) < 0.25, "Execution time on 1500 signals in the list takes more than 0.25 s."

    def test_data_with_nan(self):
        data = make_toy_data_with_nan(6)
        tests = ["local_range_test", "global_range_test", "argo_spike_test", "frozen_test"]
        flags = QC.execute(platform=qclib.QC.init(platform_code), qc_input=data,
                           measurement_name="temperature", tests=tests)
        assert flags['global_range_test'] == [1, 1, None, 1, 1, 1], "Global range test failed"
        assert flags['local_range_test'] == [1, 1, None, 1, 1, 1], "Local range test failed"
        assert flags['argo_spike_test'] == [0, 1, None, 1, 1, 0], "Argo spike test failed"
        assert flags['frozen_test'] == [0, 0, None, 0, 0, 1], "Frozen test failed"
        final_flag = PlatformQC.get_overall_flag(flags)
        assert final_flag == [0, 0, None, 0, 0, 0], "Final flag calculation failed"

    def test_flatness_test(self):
        filename = os.path.join(ORIGIN_DIR, "depth_SG.csv")
        input_data = read_testdata(filename)
        values = [(datetime.strptime(item[0].split('.')[0], '%Y-%m-%dT%H:%M:%S'), float(item[1])) for item in
                  input_data]

        flags = QCTests.flatness_test(data=QCInput(values=values, locations=None),
                                      max_variance=qclib.utils.Thresholds.flatness_max_variance)
        assert flags == [1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

    def test_pump_history_test(self):
        filename = os.path.join(ORIGIN_DIR, "ferrybox_pump_data.csv")
        input_data = read_testdata(filename)
        values = [(datetime.fromisoformat(item[0]), float(item[1])) for item in input_data]

        flags = QCTests.pump_history_test(QCInput(values=values, locations=None))
        assert flags == [-1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1]

    def test_pump_history_test_should_handle_nones(self):
        time_stamp = datetime(2018, 4, 10, 17, 45)
        values = [(time_stamp + timedelta(seconds=i), 1) for i in range(0, 15)]
        qc_input = QCInput(values=values, locations=None)
        flags = QCTests.pump_history_test(qc_input)

        # we expect the 10th flag and the following flags == 1 as the previous 9 pump values are 1
        expected = [-1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1]
        assert flags == expected

        # setting the second value to None
        qc_input.values[1] = (qc_input.values[1][0], None)

        flags2 = QCTests.pump_history_test(qc_input)

        # expect the 12th flags and following to be 1, as the second pump value is None
        expected2 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1]
        assert flags2 == expected2

    def test_executing_qc_for_pump_should_strip_nones(self):
        time_stamp = datetime(2018, 4, 10, 17, 45)
        values = [(time_stamp + timedelta(seconds=i), 1) if i % 2 == 0 else (time_stamp + timedelta(seconds=i), None)
                  for i in range(0, 25)]

        flags = QC.execute(platform=qclib.QC.init(platform_code),
                           qc_input=QCInput(values=values, locations=None),
                           measurement_name="pump",
                           tests=["pump_history_test"])
        assert flags["pump_history_test"] == [-1, None, -1, None, -1, None, -1, None, -1, None, -1, None, -1, None, -1,
                                              None, -1, None, 1, None, 1, None, 1, None, 1], "pump_history_test_failed"


if __name__ == '__main__':
    unittest.main()
