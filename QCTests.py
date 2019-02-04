'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>


Quality control tests to be applied on data. 
Tests are implemented according to the document  
Quality Control of Biogeochemical Measurements

Source documents:
Source 1 https://archimer.ifremer.fr/doc/00251/36232/34792.pdf 
[2 MyOcean] http://www.coriolis.eu.org/content/download/4920/36075/file/Recommendations%20for%20RTQC%20procedures_V1_2.pdf 



Created on 6. feb. 2018
'''

import numpy as np
import matplotlib as mpl
import time 
import pandas as pd 
from Thresholds import Local_Threshold_Ranges,Global_Threshold_Ranges
import functools
import logging

class QCTests(object):
    """
    Real Time QC Tests 
    These tests are applied to one signal
    (data aggregated during N #check minutes and sent to the cloud)
    
    The standard calling syntax for these tests is :    
      obj.specific_qc_test_function(meta, data, **opts)
    
    where        

      df: data and supporting data (meta) of the parameter to be tested . 
          some tests require a data structure or aggregation

      opts: options specific to the test, for example threshold values
        
    Return value from tests is an array of np.int8
    where 1 is PASSED, -1 is FAILED and 0 is not tested.
    """

    def check_size(size):
        def check_data_size(func):
            @functools.wraps(func)
            def func_wrapper(clf, *args, **opts):
                if len(args[0]) < size:
#FIXME distinguish cases when fetching data failed (raise error) and when there is no data (ship just started,...)
#                raise Exception("Too few data points to perform this test")
                    logging.warn("Too few data points to perform this test")
                return func(clf, *args, **opts)
            func_wrapper.size = size
            return func_wrapper
        return check_data_size



    @classmethod
    @check_size(1)
    def range_test(clf, df, **opts):
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
        Data:
        * time: corresponding array of time (relative to 1950-01-01)
        * lat : corresponding array of latitudes
        * lon : corresponding array of longitudes           
        * data: measured data (eg. salinity, or temperature,...)
        """
        
        good = np.zeros(len(df["data"]), dtype=np.int8)
        mask = np.ones(len(df["data"]), dtype=np.bool)

        if 'months' in opts and ('time' in df.columns):
            meta_months = pd.Series([
            time.strptime(n,'%Y-%m-%dT%H:%M:%S').tm_mon for n in df['time']])
            mask &= meta_months.isin(opts['months'])

        if ('area' in opts):
            lon = opts['area']['lon']
            lat = opts['area']['lat']
            npt = len(lon)
            vrt = np.ones([npt+1,2], dtype=np.float64)
            vrt[0:npt,0] = lon
            vrt[0:npt,1] = lat
            vrt[npt,0:2] = [ lon[0], lat[0] ]
            path = mpl.path.Path(vrt)
            pts = np.ones([len(df['lon']), 2])
            pts[:,0] = df["lon"]
            pts[:,1] = df['lat']
            inside = path.contains_points(pts)
            mask &= inside


        good[mask] = -1
        if 'min' in opts:
            mask &= (df["data"] >= opts['min'])
        if 'max' in opts:
            mask &= (df["data"] <= opts['max'])
        good[mask] = 1
        
        return(good)


    @classmethod
    @check_size(1)
    def missing_value_test(clf, df, **opts):
        """
        Test data for a specific value defined for missing data.        
        Options:
          nan: value used for missing data
        """
        good = np.ones(len(df["data"]), dtype=np.int8)
        mask = (df["data"] == opts['nan'])
        good[mask] = -1
        return(good)

    @classmethod
    @check_size(5)
    def RT_frozen_test(cls, df, **opts):
        """
        df[0] - last timestamp!
        Consecutive data with exactly the same value are flagged as bad
        """
        flags = np.zeros(len(df["data"]), dtype=np.int8) 
        d = df['data']
        if len(d) < 5: 
            print ('not enough data points')
        elif len(d) == 5: 
            v = all(d[n] == d[n+1] for n in range(4))
            if v:
                flags[:] = -1
        elif len(d) > 5:        
            for i in range(len(d) - 4):
                #n = i 
                v = all(d[n] == d[n+1] for n in np.arange(i,i+4))
                if v:
                    # assign -1 flag
                    flags[i] = -1
                else:
                    flags[i] = 1
            
        return flags
   
    @classmethod
    @check_size(1)
    def aic_spike_test(clf, data, **opts):
        """
        Executes spike test using an estimate of 
        Aikake Information Criterion.      
        This methods requires the last 4 points prior to the
        first point to test.
        """
        good = np.zeros(len(data), dtype=np.int8)
        mask = np.zeros(len(data), dtype=np.bool)
        ii = range(4,len(data))
        for i in ii:
            jj = range(4)
            ig = i - range(1,5)
            sg = np.std(data[ig])
            ib = i - range(5)
            sb = np.std(data[ib])
            Ug = 4*np.log(sg)
            Ub = 4*np.log(sb) - self.COEF_SPIKE
            if (Ug < Ub):
                good[i] = -1
            else:
                good[i] = 1
        return(good)
    
    @classmethod
    @check_size(1)
    def bioargo_spike_test(clf, data, **opts):
        """
        Spike test according to BIO ARGO
        
        Options:
          p10_min: factor for minimum 10 percentile 
          median difference
          p10_max: factor for maximum 10 percentile 
          median difference
          p90_min: factor for minimum 90 percentile 
          median difference
          p90_max: factor for maximum 90 percentile 
          median difference
        """
        good = np.ones(len(data), dtype=np.int8)
        diff = np.zeros(len(data), dtype=np.float64)
        ii   = range(2,len(data)-2)
        for i in ii:
            jj = range(i-2,i+2)
            diff[i] = data[i] - np.median(data[jj])
        p10  = np.percentile(diff,10)
        p90  = np.percentile(diff,90)
        mask = np.ones(len(data), dtype=np.bool)
        if 'p10_min' in opts:
            mask &= (diff >= opts['p10_min']*p10)
        if 'p10_max' in opts:
            mask &= (diff <= opts['p10_max']*p10)
        if 'p90_min' in opts:
            mask &= (diff >= opts['p90_min']*p90)
        if 'p90_max' in opts:
            mask &= (diff <= opts['p90_max']*p90)
        good[~mask] = -1
        good[:2]  = 0
        good[-2:] = 0
        return(good)
    
    @classmethod
    @check_size(5)
    def argo_spike_test(clf, data, **opts):
        """
        Spike test according to [2 MyOcean] for T and S parameters

        Options:
          threshold: threshold for consecutive double 3-values differences
          returns an array of flags with 0 to not tested parts. 
          current point (last) will always have 0 
          Flags are changes for first timestamps from 0 to tested new
          value 
        """
        good = np.ones(len(data), dtype=np.int8)
        diff = np.zeros(len(data), dtype=np.float64)
        ii   = range(1,len(data)-1)
        for i in ii:
            diff[i] = np.abs(data[i] - 0.5*(data[i-1]+data[i+1])) - 0.5*np.abs(data[i+1]-data[i-1])
        mask = (diff >= opts['threshold'])
        good[mask] = -1
        good[0]  = 0
        good[-1] = 0
        return(good)
        
    @classmethod
    @check_size(1)
    def sensor_comparison_test(clf, data, **opts):
        """
        Check whether two sensors measuring the same parameter
        provide a similar value.        
        Argument data is a tuple (s1, s2) with measurement vectors
        from sensor 1 and sensor 2 respectively.         
        Options:
          threshold: maximum difference allowed
          
          
        Here the data dataframe should be changed in order 
        to have two dependent parameters   
          
        """
        good = np.ones(data.shape[0], dtype=np.int8)
        diff = np.abs(data[1]-data[0])
        mask = (diff > opts['threshold'])
        good[mask] = -1
        return(good)
    
    @classmethod
    @check_size(1)
    def sensor_relationship_test(clf, data, **opts):
        """
        Check if the relationship between related parameters is within a certain value.
        
        Argument data is a tuple (p1, p2) with vectors of measurements from parameter 1 and 
        parameter 2 respectively.
        Here the data dataframe should be changed in order 
        to have two dependent parameters     
                     
        Options:
          p1_min: minimum difference allowed for parameter p1
          p1_max: maximum difference allowed for parameter p1
          p2_min: minimum difference allowed for parameter p2
          p2_max: maximum difference allowed for parameter p2
                    
        """
        good = np.ones(data.shape[0], dtype=np.int8)
        mask = np.ones(data.shape[0], dtype=np.bool)
        if 'p1_min' in opts:
            mask &= (data[0] >= opts['p1_min'])
        if 'p1_max' in opts:
            mask &= (data[0] <= opts['p1_max'])
        if 'p2_min' in opts:
            mask &= (data[1] >= opts['p2_min'])
        if 'p2_max' in opts:
            mask &= (data[1] <= opts['p2_max'])
        good[~mask] = -1
        return(good)
    

    
    @classmethod
    @check_size(1)
    def DM_frozen_test(cls, meta, data, **opts): #self,
        """
        Consecutive data with exactly the same value are flagged as bad.
        For the delayed mode we should add more datapoints 
        """
        good = np.ones(len(data), dtype=np.int8) #typo)? 
        mask = (np.diff(data[:]) == 0.0)
        mask = np.concatenate((mask[0:1], mask))
        good[mask] = -1
        return(good)

    
    @classmethod
    @check_size(1)
    def argo_gradient_test(clf, meta, data, **opts):
        """
        Gradient test according to BIO ARGO
        
        Options:
          threshold: threshold for consecutive 3-values difference
        """
        good = np.ones(len(data),  dtype=np.int8)
        diff = np.zeros(len(data), dtype=np.float64)
        ii   = range(1,len(data)-1)
        for i in ii:
            diff[i] = np.abs(data[i] - 0.5*(data[i-1]+data[i+1]))
        mask = (diff >= opts['threshold'])
        good[mask] = -1
        good[0]  = 0
        good[-1] = 0
        return(good)
    
    @classmethod
    @check_size(5)
    def frozen_profile_test(clf, meta, data, **opts):
        """
        Test for frozen profiles.In this case,
        data is a tuple with (depth, data) 
        where depth and data are vectors of the same length. 
        ! This test flags the whole profile.
        
        Options:
            mean_delta: max value for the mean profile difference
            min_delta : max value for the minimum profile difference
            max_delta : max value for the maximum profile difference          
        Meta:
            previous_profile: similar data tuple for the previous profile
        """
        good = np.zeros(data.shape[0], dtype=np.int8)
        if 'previous_profile' in meta:
            prev = meta['previous_profile']
            zmax = min([np.max(data[0], prev[0])])
            slab = range(0,zmax,50)
            diff = np.zeros(len(slab), dtype=np.float64)
            for i in range(len(slab)):
                zmin = slab[i]
                zmax = zmin + 50
                ii = (data[0] >= zmin) & (data[0] < zmax)
                jj = (prev[0] >= zmin) & (prev[0] < zmax)
                if not np.any(ii) or not np.any(jj):
                    diff[i] = np.nan
                    break
                else:
                    diff[i] = np.median(data[1][ii]) - np.median(prev[1][jj])
            if not np.any(np.isnan(diff)):
                good  = np.ones(len(data), dtype=np.int8)
                test  = (np.mean(diff) <= opts['delta_mean'])
                test &= (np.min(diff)  <= opts['delta_min'])
                test &= (np.max(diff)  <= opts['delta_max'])
                if not test:
                    good *= -1
        return(good)     
    


