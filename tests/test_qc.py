import unittest
import qclib.QC
from qclib.utils.qc_input import qcinput
import qclib.utils.Thresholds
from datetime import datetime, timedelta
from qclib import QC
import time

platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests
base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)


def make_toy_data(size):
    values = [[base_time + d * i, i] for i in range(0, size)]
    location = [[base_time + d * i, 10.708 + i * 0.01, 61 + i * 0.01] for i in range(0, size)]
    return qcinput(values=values, locations=location)


class Tests(unittest.TestCase):

    def test_local_range_test_for_list(self):
        data = make_toy_data(1500)
        tests = {"temperature": ["local_range_test", "global_range_test", "argo_spike_test", "frozen_test",
                                 "missing_value_test"]}
        start = time.time()
        flags = QC.execute(qclib.QC.init(platform_code), data, tests)
        end = time.time()
        print(f"time {end - start}")


if __name__ == '__main__':
    unittest.main()
