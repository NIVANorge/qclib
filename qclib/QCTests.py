'''
Tests are implemented according to the document
Quality Control of Biogeochemical Measurements
[1] http://archimer.ifremer.fr/doc/00251/36232/34792.pdf  
[2] http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf
'''
import numpy as np
from .utils.qc_input import qcinput
from .utils.qctests_helpers import is_inside_geo_region
import functools
import logging
from .utils.validate_input import validate_data_for_argo_spike_test, validate_data_for_frozen_test


class QCTests(object):
    """
    Real Time QC Tests 
    These tests are applied to one signal ( = one timestamp)
    Return value of each test is an integer: 0= test not ran, -1=test failed, 1= test succeeded
    """

    def check_size(number_of_historical, number_of_future):
        def check_data_size(func):
            @functools.wraps(func)
            def func_wrapper(clf, *args, **opts):
                if number_of_historical > 0:
                    if args[0].historical_data is None:
                        logging.debug("No historical data available to perform %s test" % func.__name__)
                    elif len(args[0].historical_data) < number_of_historical:
                        logging.debug("Too few historical data points to perform %s test" % func.__name__)
                if number_of_future > 0:
                    if args[0].future_data is None:
                        logging.debug("No future data available to perform %s test" % func.__name__)
                    elif len(args[0].future_data) < number_of_future:
                        logging.debug("Too few future data points to perform %s test" % func.__name__)
                return func(clf, *args, **opts)

            func_wrapper.number_of_historical = number_of_historical
            func_wrapper.number_of_future = number_of_future
            return func_wrapper

        return check_data_size

    @classmethod
    @check_size(1, 1)
    def argo_spike_test(clf, data: qcinput, **opts) -> int:
        """
        Spike test according to MyOcean [2] for T and S parameters
        The same test for Oxygen is defined at Bio Argo
        Options:
          threshold: threshold for consecutive double 3-values differences
        """

        flag = np.zeros(len(data.values), dtype=np.int)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        is_valid &= validate_data_for_argo_spike_test(data)

        # is_valid is an array with boolean describing weather current point has valid historical and future point.

        def k_diff(val, index):
            if index == 0 or index == len(val) - 1:
                return 0
            else:
                return np.abs(val[index] - 0.5 * (val[index + 1] + val[index - 1])) \
                       - 0.5 * np.abs(val[index + 1] - val[index - 1])

        k_diff_list = [k_diff(data.values[:, 1], index) for index in range(0, len(data.values))]
        k_diff_array = np.array(k_diff_list)

        flag[is_valid] = -1
        is_valid &= (k_diff_array < opts['spike_threshold'])
        flag[is_valid] = 1
        return flag

    @classmethod
    @check_size(0, 0)
    def range_test(clf, data: qcinput, **opts) -> [int]:
        """

        """

        if 'area' in opts and 'months' in opts:
            assert len(data.values) == len(data.locations), "Invalid geographical coordinates:" \
                                                            "Location and values list have different length."

        flag = np.zeros(len(data.values), dtype=np.int8)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        values = np.array(data.values)

        if 'months' in opts:
            is_valid &= [values[i][0].month in opts['months'] for i in range(0, len(values))]

        if 'area' in opts:
            is_valid &= is_inside_geo_region(data.locations, **opts)

        flag[is_valid] = -1
        if 'min' in opts:
            is_valid &= (values[:, 1] >= opts['min'])
        if 'max' in opts:
            is_valid &= (values[:, 1] <= opts['max'])

        flag[is_valid] = 1
        return flag

    @classmethod
    @check_size(4, 0)
    def frozen_test(cls, data: qcinput) -> int:
        """
        Consecutive data with exactly the same value are flagged as bad
        """
        flag = np.zeros(len(data.values), dtype=np.int)
        is_valid = np.ones(len(data.values), dtype=np.bool)
        size_historical = QCTests.frozen_test.number_of_historical
        is_valid &= validate_data_for_frozen_test(data, size_historical)
        # is_valid is an array with boolean describing weather current point has valid historical and future point.

        flag[is_valid] = -1
        data_diff = np.diff(np.array(data.values)[:, 1])
        is_frozen = [True for i in range(0, size_historical)] + \
                    [all(data_diff[-size_historical + i:i] != 0.0) for i in range(size_historical, len(data.values))]

        is_valid &= np.array(is_frozen)
        flag[is_valid] = 1
        return flag
