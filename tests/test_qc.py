import csv
import os
import time
import unittest
from datetime import datetime, timedelta

import qclib.utils.Thresholds
from qclib import QC
from qclib.utils.qc_input import QCInput

platform_code = 'TF'
common_tests = QC.init(platform_code).qc_tests
base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)


def make_toy_data(size):
    values = [[base_time + d * i, i] for i in range(0, size)]
    location = [(base_time + d * i, 10.708 + i * 0.01, 61 + i * 0.01) for i in range(0, size)]
    return QCInput(values=values, locations=location)


def read_testdata(filename):
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        return list(csv_reader)[1:]


class Tests(unittest.TestCase):

    def test_qc_logic(self):
        origin_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata")
        filename = os.path.join(origin_dir, "ferrybox_data.csv")
        input_data = read_testdata(filename)
        values = [[datetime.strptime(item[0].split('.')[0], '%Y-%m-%dT%H:%M:%S'), float(item[1])] for item in
                  input_data]
        ref_frozen_test = [int(item[2]) for item in input_data]
        ref_global_range_test = [int(item[3]) for item in input_data]
        ref_argo_spike_test = [int(item[4]) for item in input_data]
        locations = None
        flags = QC.execute(qclib.QC.init(platform_code), QCInput(values=values, locations=locations),
                           tests={"salinity": ["global_range_test", "frozen_test", "argo_spike_test"]})

        assert flags["frozen_test"] == ref_frozen_test, "Frozen test failed"
        assert flags["global_range_test"] == ref_global_range_test, "Global range test failed"
        assert flags["argo_spike_test"] == ref_argo_spike_test, "Argo spike test failed"

    def test_execution_time_with_toy_data(self):
        data = make_toy_data(1500)
        tests = {"temperature": ["local_range_test", "global_range_test", "argo_spike_test", "frozen_test"]}
        start = time.time()
        QC.execute(qclib.QC.init(platform_code), data, tests)
        end = time.time()
        assert (end - start) < 0.2, "Execution time on 1500 is slow"


if __name__ == '__main__':
    unittest.main()
