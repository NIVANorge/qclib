'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>


Quality control tests to be applied on data. 
Tests are implemented according to the document  
Quality Control of Biogeochemical Measurements
http://archimer.ifremer.fr/doc/00251/36232/34792.pdf  

Created on 6. feb. 2018
'''

import numpy as np
import matplotlib as mpl
import time
import pandas as pd
from .utils.qc_input import QCInput
import functools
import logging
from .utils.transform_input import merge_data, validate_data_for_time_gaps


class QCTests(object):
    """
    Real Time QC Tests 
    These tests are applied to one signal
    (data aggregated during 15 minutes and sent to the cloud 
    
    Specific tests are defined here. Add whatever new tests. 
    The standard calling syntax for these tests is :    
      obj.specific_qc_test_function(meta, data, **opts)
    
    where        
      meta: a dict including any meta information required to perform the test,
            for example position and time (see specific tests below)
      data: normally, this is the data of the parameter to be tested. 
            However. some tests require a data structure or aggregation.
      opts: options specific to the test, for example threshold values
        
    Return value from tests is an array of np.int8
    where 1 is PASSED, -1 is FAILED and 0 is not tested.
    """

    def check_size(size):
        def check_data_size(func):
            @functools.wraps(func)
            def func_wrapper(clf, *args, **opts):
                if size > 1:
                    if args[0].historical_data is None:
                        logging.warning("No historical data available to perform %s test" % func.__name__)
                    elif len(args[0].historical_data)+1 < size:
                        logging.warning("Too few data points to perform %s test" % func.__name__)
                return func(clf, *args, **opts)
            func_wrapper.size = size
            return func_wrapper

        return check_data_size

    @classmethod
    @check_size(1)
    def rt_range_test(clf, qcinput, **opts) -> int:
        # FIXME since this test runs now per point, its definition can be significantly simplified
        """
        4.4 Global Range Tests 
        4.5 Local Range Tests 
        
        Checks that data is within a specified range.Accepts time range 
        and geographic range. The latter is based on minimum and maximum 
        latitudes and longitudes values. An later improvement could be
        to accept a geographic box.  
        
        Options:         
        * min    : minimum value (inclusive)
        * max    : maximum value (inclusive)
        * day_min: minimum date for which the test applies,
                   can be `py:class:datetime.date` or a decimal date
                   relative to 1950-01-01
        * day_max: maximum date for which the test applies (same format as `day_min`) 
        * lat_min: minimum latitude for which the test applies
        * lat_max: maximum latitude for which the test applies
        * lon_min: minimum longitude for which the test applies
        * lon_max: maximum longitude for which the test applies
        * area   : dictionary of polygon edges, with keys 'lat' and 'lon'. 
                   These should be listed in CW order
        """
        df = pd.DataFrame.from_dict({"data": [qcinput.value], "time": [qcinput.timestamp]})
        good = np.zeros(len(df["data"]), dtype=np.int8)
        mask = np.ones(len(df["data"]), dtype=np.bool)

        if 'months' in opts and ('time' in df.columns):
            meta_months = pd.Series([
                time.strptime(str(n), '%Y-%m-%d %H:%M:%S').tm_mon for n in df['time']])
            mask &= meta_months.isin(opts['months'])

        if ('area' in opts):
            lon = opts['area']['lon']
            lat = opts['area']['lat']
            npt = len(lon)
            vrt = np.ones([npt + 1, 2], dtype=np.float64)
            vrt[0:npt, 0] = lon
            vrt[0:npt, 1] = lat
            vrt[npt, 0:2] = [lon[0], lat[0]]
            path = mpl.path.Path(vrt)
            pts = np.ones([len(df), 2])
            pts[:, 0] = qcinput.longitude
            pts[:, 1] = qcinput.latitude
            inside = path.contains_points(pts)
            mask &= inside

        good[mask] = -1
        if 'min' in opts:
            mask &= (df["data"] >= opts['min'])
        if 'max' in opts:
            mask &= (df["data"] <= opts['max'])
        good[mask] = 1

        return int(good[0])

    @classmethod
    @check_size(1)
    def rt_missing_value_test(clf, qcinput, **opts)->int:
        """
        Test data for a specific value defined for missing data.        
        Options:
          nan: value used for missing data
        """
        flag = 1
        if qcinput.value == opts['nan']:
            flag = -1
        return flag

    @classmethod
    @check_size(5)
    def rt_frozen_test(cls, qcinput: QCInput) -> int:
        """
        Consecutive data with exactly the same value are flagged as bad
        """
        # FIXME: get size below from decorator (if possible)
        size = 5
        df = pd.DataFrame.from_dict({"data": [qcinput.value], "time": [qcinput.timestamp]})
        df_delayed = qcinput.historical_data
        data = merge_data(df, df_delayed)
        validate_data_for_time_gaps(data)
        flag = 1
        if len(data["data"]) < size:
            flag = 0
        else:
            data_diff = data["data"].diff().dropna()
            if all(data_diff[-size+1:]) == 0.0:
                flag = -1
        return flag


    # @classmethod
    # @check_size(1)
    # def missing_value_test_array(clf, qcinput, **opts):
    #      """
    #         Test data for a specific value defined for missing data.
    #         Options:
    #           nan: value used for missing data
    #         """
    #
    #     df = pd.DataFrame.from_dict({"data": qcinput.value, "time": qcinput.timestamp})
    #     good = np.ones(len(df["data"]), dtype=np.int8)
    #     mask = (df["data"] == opts['nan'])
    #     good[mask] = -1
    #     return good

        # @classmethod
    # @check_size(1)
    # def aic_spike_test(clf, data, **opts):
    #     """
    #     Executes spike test using an estimate of
    #     Aikake Information Criterion.
    #     This methods requires the last 4 points prior to the
    #     first point to test.
    #     """
    #     good = np.zeros(len(data), dtype=np.int8)
    #     mask = np.zeros(len(data), dtype=np.bool)
    #     ii = range(4, len(data))
    #     for i in ii:
    #         jj = range(4)
    #         ig = i - range(1, 5)
    #         sg = np.std(data[ig])
    #         ib = i - range(5)
    #         sb = np.std(data[ib])
    #         Ug = 4 * np.log(sg)
    #         Ub = 4 * np.log(sb) - self.COEF_SPIKE
    #         if (Ug < Ub):
    #             good[i] = -1
    #         else:
    #             good[i] = 1
    #     return (good)
    #
    # @classmethod
    # @check_size(1)
    # def bioargo_spike_test(clf, data, **opts):
    #     """
    #     Spike test according to BIO ARGO
    #
    #     Options:
    #       p10_min: factor for minimum 10 percentile
    #       median difference
    #       p10_max: factor for maximum 10 percentile
    #       median difference
    #       p90_min: factor for minimum 90 percentile
    #       median difference
    #       p90_max: factor for maximum 90 percentile
    #       median difference
    #     """
    #     good = np.ones(len(data), dtype=np.int8)
    #     diff = np.zeros(len(data), dtype=np.float64)
    #     ii = range(2, len(data) - 2)
    #     for i in ii:
    #         jj = range(i - 2, i + 2)
    #         diff[i] = data[i] - np.median(data[jj])
    #     p10 = np.percentile(diff, 10)
    #     p90 = np.percentile(diff, 90)
    #     mask = np.ones(len(data), dtype=np.bool)
    #     if 'p10_min' in opts:
    #         mask &= (diff >= opts['p10_min'] * p10)
    #     if 'p10_max' in opts:
    #         mask &= (diff <= opts['p10_max'] * p10)
    #     if 'p90_min' in opts:
    #         mask &= (diff >= opts['p90_min'] * p90)
    #     if 'p90_max' in opts:
    #         mask &= (diff <= opts['p90_max'] * p90)
    #     good[~mask] = -1
    #     good[:2] = 0
    #     good[-2:] = 0
    #     return (good)
    #
    # @classmethod
    # @check_size(1)
    # def argo_spike_test(clf, data, **opts):
    #     """
    #     Spike test according to MyOcean for T and S parameters
    #     http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf
    #     Options:
    #       threshold: threshold for consecutive double 3-values differences
    #     """
    #     good = np.ones(len(data), dtype=np.int8)
    #     diff = np.zeros(len(data), dtype=np.float64)
    #     ii = range(1, len(data) - 1)
    #     for i in ii:
    #         diff[i] = np.abs(data[i] - 0.5 * (data[i - 1] + data[i + 1])) - 0.5 * np.abs(data[i + 1] - data[i - 1])
    #     mask = (diff >= opts['threshold'])
    #     good[mask] = -1
    #     good[0] = 0
    #     good[-1] = 0
    #     return (good)
    #
    # @classmethod
    # @check_size(1)
    # def sensor_comparison_test(clf, data, **opts):
    #     """
    #     Check whether two sensors measuring the same parameter
    #     provide a similar value.
    #     Argument data is a tuple (s1, s2) with measurement vectors
    #     from sensor 1 and sensor 2 respectively.
    #     Options:
    #       threshold: maximum difference allowed
    #
    #
    #     Here the data dataframe should be changed in order
    #     to have two dependent parameters
    #
    #     """
    #     good = np.ones(data.shape[0], dtype=np.int8)
    #     diff = np.abs(data[1] - data[0])
    #     mask = (diff > opts['threshold'])
    #     good[mask] = -1
    #     return (good)
    #
    # @classmethod
    # @check_size(1)
    # def sensor_relationship_test(clf, df, **opts):
    #     """
    #     Check if the relationship between related parameters is within a certain value.
    #
    #     Argument data is a tuple (p1, p2) with vectors of measurements from parameter 1 and
    #     parameter 2 respectively.
    #     Here the data dataframe should be changed in order
    #     to have two dependent parameters
    #
    #     Options:
    #       p1_min: minimum difference allowed for parameter p1
    #       p1_max: maximum difference allowed for parameter p1
    #       p2_min: minimum difference allowed for parameter p2
    #       p2_max: maximum difference allowed for parameter p2
    #
    #     """
    #     good = np.ones(data.shape[0], dtype=np.int8)
    #     mask = np.ones(data.shape[0], dtype=np.bool)
    #     if 'p1_min' in opts:
    #         mask &= (data[0] >= opts['p1_min'])
    #     if 'p1_max' in opts:
    #         mask &= (data[0] <= opts['p1_max'])
    #     if 'p2_min' in opts:
    #         mask &= (data[1] >= opts['p2_min'])
    #     if 'p2_max' in opts:
    #         mask &= (data[1] <= opts['p2_max'])
    #     good[~mask] = -1
    #     return (good)
    #
    # @classmethod
    # @check_size(1)
    # def DM_frozen_test(cls, meta, data, **opts):  # self,
    #     """
    #     Consecutive data with exactly the same value are flagged as bad.
    #     For the delayed mode we should add more datapoints
    #     """
    #     good = np.ones(len(data), dtype=np.int8)  # typo)?
    #     mask = (np.diff(data[:]) == 0.0)
    #     mask = np.concatenate((mask[0:1], mask))
    #     good[mask] = -1
    #     return (good)
    #
    # @classmethod
    # @check_size(1)
    # def argo_gradient_test(clf, meta, data, **opts):
    #     """
    #     Gradient test according to BIO ARGO
    #
    #     Options:
    #       threshold: threshold for consecutive 3-values difference
    #     """
    #     good = np.ones(len(data), dtype=np.int8)
    #     diff = np.zeros(len(data), dtype=np.float64)
    #     ii = range(1, len(data) - 1)
    #     for i in ii:
    #         diff[i] = np.abs(data[i] - 0.5 * (data[i - 1] + data[i + 1]))
    #     mask = (diff >= opts['threshold'])
    #     good[mask] = -1
    #     good[0] = 0
    #     good[-1] = 0
    #     return (good)
    #
    # @classmethod
    # @check_size(5)
    # def frozen_profile_test(clf, meta, data, **opts):
    #     """
    #     Test for frozen profiles.In this case,
    #     data is a tuple with (depth, data)
    #     where depth and data are vectors of the same length.
    #     ! This test flags the whole profile.
    #
    #     Options:
    #         mean_delta: max value for the mean profile difference
    #         min_delta : max value for the minimum profile difference
    #         max_delta : max value for the maximum profile difference
    #     Meta:
    #         previous_profile: similar data tuple for the previous profile
    #     """
    #     good = np.zeros(data.shape[0], dtype=np.int8)
    #     if 'previous_profile' in meta:
    #         prev = meta['previous_profile']
    #         zmax = min([np.max(data[0], prev[0])])
    #         slab = range(0, zmax, 50)
    #         diff = np.zeros(len(slab), dtype=np.float64)
    #         for i in range(len(slab)):
    #             zmin = slab[i]
    #             zmax = zmin + 50
    #             ii = (data[0] >= zmin) & (data[0] < zmax)
    #             jj = (prev[0] >= zmin) & (prev[0] < zmax)
    #             if not np.any(ii) or not np.any(jj):
    #                 diff[i] = np.nan
    #                 break
    #             else:
    #                 diff[i] = np.median(data[1][ii]) - np.median(prev[1][jj])
    #         if not np.any(np.isnan(diff)):
    #             good = np.ones(len(data), dtype=np.int8)
    #             test = (np.mean(diff) <= opts['delta_mean'])
    #             test &= (np.min(diff) <= opts['delta_min'])
    #             test &= (np.max(diff) <= opts['delta_max'])
    #             if not test:
    #                 good *= -1
    #     return (good)