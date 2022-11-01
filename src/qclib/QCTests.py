"""
Tests are implemented according to the document
Quality Control of Biogeochemical Measurements
[1] http://archimer.ifremer.fr/doc/00251/36232/34792.pdf
[2] http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf
"""
import functools
from typing import List

import numpy as np

from qclib.utils.qc_input import QCInput
from qclib.utils.qctests_helpers import is_inside_geo_region
from qclib.utils.validate_input import validate_data_for_argo_spike_test, initial_flags_for_historical_test


def qctest_additional_data_size(number_of_historical=0, number_of_future=0):
    """Decorator. Adds parameters to the decorated function/method."""
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

        flag = np.zeros(len(data.values), dtype=int)
        is_valid = np.ones(len(data.values), dtype=bool)
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
        flag = np.zeros(len(data.values), dtype=int)
        is_valid = np.ones(len(data.values), dtype=bool)
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
    def frozen_test(cls, qc_input: QCInput) -> List[int]:
        """Consecutive data with exactly the same value are flagged as bad"""
        size_historical = QCTests.frozen_test.number_of_historical

        if len(qc_input.values) < size_historical:
            return [0 for _ in range(len(qc_input.values))]

        flag_array = initial_flags_for_historical_test(qc_input, size_historical, 2.1)

        data_diff = np.diff(np.array(qc_input.values)[:, 1].astype(float))

        sensor_has_been_frozen = [all(data_diff[-size_historical + i: i] == 0.0)
                                  for i in range(size_historical, len(qc_input.values))]
        flag_array[[False] * size_historical + sensor_has_been_frozen] = -1
        return list(flag_array.tolist())

    @classmethod
    @qctest_additional_data_size(number_of_historical=4)
    def flatness_test(cls, data: QCInput, max_variance) -> List[int]:
        """This test flags 'flat' data as bad. If the variance is below max_variance flag = -1"""
        flag = np.zeros(len(data.values), dtype=int)
        is_valid = np.ones(len(data.values), dtype=bool)
        size = QCTests.flatness_test.number_of_historical
        data = np.array(data.values)[:, 1].astype(float)
        if len(data) < size:
            size = len(data) - 1
        is_flat = [False] * size + \
                  [data[-size + i: i].var() < max_variance for i in range(size, len(data))]
        flag[is_valid] = 1
        is_valid &= np.array(is_flat)
        flag[is_valid] = -1
        # noinspection PyTypeChecker
        return flag.tolist()

    @classmethod
    @qctest_additional_data_size(number_of_historical=3)
    def bounded_variance_test(cls, qc_input: QCInput, max_variance: float) -> List[int]:
        """Consecutive data with variance above max_variance are flagged as bad."""
        size_historical = QCTests.bounded_variance_test.number_of_historical
        values = np.array(qc_input.values)[:, 1].astype(float)

        if len(values) < size_historical:
            return [0 for _ in range(len(values))]

        flag_array = initial_flags_for_historical_test(qc_input, size_historical, 2.1)

        variance_array = [values[i - size_historical: i].var() for i in range(size_historical, len(values))]
        variance_too_large = [False] * size_historical + [var > max_variance for var in variance_array]
        flag_array[variance_too_large] = -1
        return list(flag_array.tolist())

    @classmethod
    @qctest_additional_data_size(number_of_historical=9)
    def pump_history_test(cls, qc_input: QCInput) -> List[int]:
        """
        Pump is on for at least 10 minutes, which is equivalent to 10 consecutive points
        with sampling interval 60s
        """
        size_historical = QCTests.pump_history_test.number_of_historical

        if len(qc_input.values) < size_historical:
            return [-1 for _ in range(len(qc_input.values))]

        flag_array = initial_flags_for_historical_test(qc_input, size_historical, 2.1)
        # For the pump history test, if we can't run the test the data counts as invalid.
        flag_array[flag_array==0] = -1

        pump_values = np.array(qc_input.values)[:, 1]
        pump_values[pump_values==None] = 0
        pump_values = pump_values.astype(int)

        pump_has_been_turned_off = [any(pump_values[-size_historical + i: i+1] == 0)
                                    for i in range(size_historical, len(qc_input.values))]
        flag_array[[False] * size_historical + pump_has_been_turned_off] = -1

        return list(flag_array.tolist())
