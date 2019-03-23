'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>
Quality control tests to be applied on data.
Tests are implemented according to the document  
Quality Control of Biogeochemical Measurements
[1] http://archimer.ifremer.fr/doc/00251/36232/34792.pdf  
[2] http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf
Created on 6. feb. 2018
'''
import numpy as np
import time
from .utils.qc_input import QCInput_df
from .utils.qctests_helpers import is_inside_geo_region
import functools
import logging
from .utils.transform_input import merge_data_spike,merge_data


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
                        logging.warning("No historical data available to perform %s test" % func.__name__)
                    elif len(args[0].historical_data) < number_of_historical:
                        logging.warning("Too few historical data points to perform %s test" % func.__name__)
                if number_of_future > 0:
                    if args[0].future_data is None:
                        logging.warning("No future data available to perform %s test" % func.__name__)
                    elif len(args[0].future_data) < number_of_future:
                        logging.warning("Too few future data points to perform %s test" % func.__name__)
                return func(clf, *args, **opts)

            func_wrapper.number_of_historical = number_of_historical
            func_wrapper.number_of_future = number_of_future
            return func_wrapper

        return check_data_size

    @classmethod
    @check_size(0, 0)
    def rt_range_test(clf, qcinput: QCInput_df, **opts) -> int:
        """

        """
        df = qcinput.current_data

        valid_opts = True
        if 'months' in opts and ('time' in df.columns):
            valid_opts = time.strptime(str(df["time"].iloc[0]), '%Y-%m-%d %H:%M:%S').tm_mon in opts['months']
        if 'area' in opts:
            valid_opts = is_inside_geo_region(qcinput.longitude, qcinput.latitude, **opts)
        if not valid_opts:
            return 0
        flag = 1
        if 'min' in opts and df["data"].iloc[0] < opts['min']:
            flag = -1
        if 'max' in opts and df["data"].iloc[0] > opts['max']:
            flag = -1

        return flag

    @classmethod
    @check_size(0, 0)
    def rt_missing_value_test(clf, qcinput: QCInput_df, **opts) -> int:
        """
        Test data for a specific value defined for missing data.        
        Options:
          nan: value used for missing data
        """
        flag = 1
        value = qcinput.current_data["data"]
        if value[0] == opts['nan']:
            flag = -1
        return flag

    @classmethod
    @check_size(4, 0)
    def rt_frozen_test(cls, qcinput: QCInput_df) -> int:
        """
        Consecutive data with exactly the same value are flagged as bad
        """
        size_historical = QCTests.rt_frozen_test.number_of_historical
        if len(qcinput.historical_data) < size_historical:
            return 0
        data = merge_data(qcinput.current_data, qcinput.historical_data)
        flag = 1
        data_diff = data["data"].diff().dropna()
        if all(data_diff[-size_historical:] == 0.0):
            flag = -1
        return flag

    @classmethod
    @check_size(1, 1)
    def argo_spike_test(clf, qcinput: QCInput_df, **opts) -> int:
        """
        Spike test according to MyOcean [2] for T and S parameters
        
        Options:
          threshold: threshold for consecutive double 3-values differences
        """

        size_historical = QCTests.argo_spike_test.number_of_historical
        size_future = QCTests.argo_spike_test.number_of_future
        if len(qcinput.historical_data) < size_historical or len(qcinput.future_data) < size_future:
            return 0

        data = merge_data_spike(qcinput.historical_data, qcinput.current_data, qcinput.future_data)['data']
        k_diff = np.abs(data[1] - 0.5 * (data[2] + data[0])) - 0.5 * np.abs(data[2] - data[0])

        if k_diff >= opts['spike_threshold']:
            flag = -1
        elif k_diff < opts['spike_threshold']:
            flag = 1
        return flag
