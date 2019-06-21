"""
Tests are implemented according to the document
Quality Control of Biogeochemical Measurements
[1] http://archimer.ifremer.fr/doc/00251/36232/34792.pdf
[2] http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf
"""
import functools
from typing import List

import numpy as np

from .utils.qc_input import QCInput
from .utils.qctests_helpers import is_inside_geo_region
from .utils.validate_input import validate_data_for_argo_spike_test, validate_data_for_frozen_test


def qctest_additional_data_size(number_of_historical=0, number_of_future=0):
    """
    Decorator. Adds parameters to the decorated function/method.
    """

    def set_parameters(func):
        @functools.wraps(func)
        def func_wrapper(cls, *args, **opts):
            return func(cls, *args, **opts)

        func_wrapper.number_of_historical = number_of_historical
        func_wrapper.number_of_future = number_of_future
        return func_wrapper

    return set_parameters


class QCTests:
    """
    Real Time QC Tests
    These tests are applied to one signal ( = one timestamp)
    Return value of each test is an integer: 0= test not ran, -1=test failed, 1= test succeeded
    """

    @classmethod
    @qctest_additional_data_size(number_of_historical=1, number_of_future=1)
    def argo_spike_test(cls, data: QCInput, **opts) -> List[int]:
        """
        Spike test according to MyOcean [2] for T and S parameters
        The same test for Oxygen is defined at Bio Argo
        Options:
          threshold: threshold for consecutive double 3-values differences
        """

        flag = np.zeros(len(data.values), dtype=np.int)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        is_valid &= validate_data_for_argo_spike_test(data)

        # is_valid is an array of booleans describing whether current point has valid historical and future points.

        def k_diff(val, index):
            if None in val[index - 1:index + 2]:
                return np.nan
            else:
                return abs(val[index] - 0.5 * (val[index + 1] + val[index - 1])) \
                   - 0.5 * abs(val[index + 1] - val[index - 1])

        values = np.array(data.values)[:, 1]
        k_diffs = np.zeros(len(data.values))
        k_diffs[1:-1] = [k_diff(values, i) for i in range(1, len(values) - 1)]

        flag[is_valid] = -1
        with np.errstate(invalid='ignore'):
            is_valid &= k_diffs < opts['spike_threshold']
        flag[is_valid] = 1

        # noinspection PyTypeChecker
        return flag.tolist()

    @classmethod
    @qctest_additional_data_size()
    def range_test(cls, data: QCInput, **opts) -> List[int]:
        """

        """

        if 'area' in opts and 'months' in opts:
            assert len(data.values) == len(data.locations), "Invalid geographical coordinates:" \
                                                            "Location and values list have different length."

        flag = np.zeros(len(data.values), dtype=np.int)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        values = np.array(data.values)

        if 'months' in opts:
            months = set(opts['months'])
            is_valid &= [value[0].month in months for value in values]

        if 'area' in opts:
            is_valid &= is_inside_geo_region(data.locations, opts['area'])

        flag[is_valid] = -1
        if 'min' in opts:
            with np.errstate(invalid='ignore'):
                is_valid &= values[:, 1].astype(float) >= opts['min']
        if 'max' in opts:
            with np.errstate(invalid='ignore'):
                is_valid &= values[:, 1].astype(float) <= opts['max']

        flag[is_valid] = 1

        # noinspection PyTypeChecker
        return flag.tolist()

    @classmethod
    @qctest_additional_data_size()
    def missing_value_test(cls, data: QCInput, **opts) -> List[int]:
        """
        Flag values that have the given magic ('nan') value
        """
        flag = np.full(len(data.values), -1, dtype=np.int)
        values = np.array(data.values)

        is_valid = values[:, 1].astype(float) != opts['nan']
        flag[is_valid] = 1

        # noinspection PyTypeChecker
        return flag.tolist()

    @classmethod
    @qctest_additional_data_size(number_of_historical=4)
    def frozen_test(cls, data: QCInput) -> List[int]:
        """
        Consecutive data with exactly the same value are flagged as bad
        """
        flag = np.zeros(len(data.values), dtype=np.int)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        size_historical = QCTests.frozen_test.number_of_historical
        is_valid &= validate_data_for_frozen_test(data, size_historical)
        # is_valid is an array with boolean describing whether current point has valid historical and future points.

        flag[is_valid] = 1
        data_diff = np.diff(np.array(data.values)[:, 1].astype(float))
        is_frozen = [True] * size_historical + \
                    [all(data_diff[-size_historical + i: i] == 0.0) for i in range(size_historical, len(data.values))]

        is_valid &= np.array(is_frozen)
        flag[is_valid] = -1

        # noinspection PyTypeChecker
        return flag.tolist()

    @classmethod
    @qctest_additional_data_size(number_of_historical=4)
    def flatness_test(cls, data: QCInput) -> List[int]:
        """
        Consecutive data with variance below 1e-5 are flagged as bad
        """
        flag = np.zeros(len(data.values), dtype=np.int)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        size = QCTests.frozen_test.number_of_historical
        data = np.array(data.values)[:, 1].astype(float)
        is_flat = [False] * size + \
                  [data[-size + i: i].var() < 1e-5 for i in range(size, len(data))]
        flag[is_valid] = 1
        is_valid &= np.array(is_flat)
        flag[is_valid] = -1
        # noinspection PyTypeChecker
        return flag.tolist()
