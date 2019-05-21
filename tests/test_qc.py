'''
Created on 15. jan. 2018
@author: ELP
'''
import unittest
import qclib.QC
from qclib.utils.qc_input import qcinput
import qclib.utils.Thresholds
from qclib import Platforms
from qclib.PlatformQC import PlatformQC
from datetime import datetime, timedelta
from qclib import QC
import qclib.utils.Thresholds as th
from qclib.QCTests import QCTests
import time
import numpy as np

platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests

base_time = datetime.strptime('2017-01-12 14:08:06', '%Y-%m-%d %H:%M:%S')
d = timedelta(seconds=60)


def make_local_range_test_data(size):
    values = [[base_time + d * i, i] for i in range(0, size)]
    location = [[base_time + d * i, 10.708 + i * 0.01, 61 + i * 0.01] for i in range(0, size)]
    return qcinput(values=values, locations=location)


class Tests(unittest.TestCase):

    def test_local_range_test_for_list(self):
        data = make_local_range_test_data(2500)
        params_t = {'min': -2.0, 'max': 24.0, 'area': th.Arctic, 'months': th.all_months}
        start = time.time()
        flag = QCTests.range_test(data, **params_t)
        end = time.time()
        print(f"time {end - start}")


if __name__ == '__main__':
    unittest.main()
