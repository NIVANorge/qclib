'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.QC
==========

Quality control tests to be applied on data. 

Created on 6. feb. 2018
'''

import math
import datetime
import numpy as np
import matplotlib as mpl
 
from pyTools.Conversions import date_to_day1950

from pyFerry.Globals import Areas
# from .Globals import Areas raised an error 


class QCTests(object):
    """
    Specific tests are defined here. Add whatever new tests. 
    The standard calling synthax for these tests is::
    
      obj.specific_qc_test_function(meta, data, **opts)
    
    where
        
      meta: a dict including any meta information required to perform the test, for example position 
              and time (see specific tests below)
      data: normally, this is the data of the parameter to be tested. However. some tests require 
            a data structure or aggregation.
      opts: options specific to the test, for example threshold values
        
    Return value from tests is an array of np.int8
    where 1 is PASSED, -1 is FAILED and 0 is not tested.
    """

    COEF_SPIKE = (math.log(120)/5)*math.sqrt(2)

    @classmethod
    def frozen_test(cls, meta, data, **opts): #self,
        """
        Consecutive data with exactly the same value are mflagged as bad.
        """
        good = np.ones(len(data), dtype=np.int8) #typo)? 
        mask = (np.diff(data[:]) == 0.0)
        mask = np.concatenate((mask[0:1], mask))
        good[mask] = -1
        return(good)
    
    @classmethod
    def range_test(clf, meta, data, **opts):
        """
        Check that data is within a specified range.
        
        Accepts time range and geographic range. The later is based on minimum and maximum latitudes and longitudes
        values. An later improvement could be to accept a geographic box.  
        
        Options:
         
        * min    : minimum value (inclusive)
        * max    : maximum value (inclusive)
        * day_min: minimum date for which the test applies, can be `py:class:datetime.date` or a decimal date
                   relative to 1950-01-01
        * day_max: maximum date for which the test applies (same format as `day_min`) 
        * lat_min: minimum latitude for which the test applies
        * lat_max: maximum latitude for which the test applies
        * lon_min: minimum longitude for which the test applies
        * lon_max: maximum longitude for which the test applies
        * area   : dictionary of polygon edges, with keys 'lat' and 'lon'. These should be listed in CW order.
        
        Meta:
        
        * time: corresponding array of time (relative to 1950-01-01)
        * lat : corresponding array of latitudes
        * lon : corresponding array of longitudes           
        """
        good = np.zeros(len(data), dtype=np.int8)
        mask = np.ones(len(data), dtype=np.bool)
        #
        if ('day_min' in opts) and ('time' in meta):
            if isinstance(opts['day_min'], datetime.date):
                opts['day_min'] = date_to_day1950(opts['day_min'])
            mask &= (meta['time'] >= opts['day_min'])
        if ('day_max' in opts) and ('time' in meta):
            if isinstance(opts['day_max'], datetime.date):
                opts['day_max'] = date_to_day1950(opts['day_max'])
            mask &= (meta['time'] <= opts['day_max'])
        #
        if ('lat_min' in opts) and ('lat' in meta):
            mask &= (meta['lat'] >= opts['lat_min'])
        if ('lat_max' in opts) and ('lat' in meta):
            mask &= (meta['lat'] <= opts['lat_max'])
        #
        if ('lon_min' in opts) and ('lon' in meta):
            mask &= (meta['lon'] >= opts['lon_min'])
        if ('lon_max' in opts) and ('lon' in meta):
            mask &= (meta['lon'] <= opts['lon_max'])
        #
        if ('area' in opts):
            lon = opts['area']['lon']
            lat = opts['area']['lat']
            npt = len(lon)
            vrt = np.ones([npt+1,2], dtype=np.float64)
            vrt[0:npt,0] = lon
            vrt[0:npt,1] = lat
            vrt[npt,0:2] = [ lon[0], lat[0] ]
            path = mpl.path.Path(vrt)
            pts = np.ones([len(meta['lon']), 2])
            pts[:,0] = meta['lon']
            pts[:,1] = meta['lat']
            inside = path.contains_points(pts)
            mask &= inside
        #
        good[mask] = -1
        #
        if 'min' in opts:
            mask &= (data >= opts['min'])
        if 'max' in opts:
            mask &= (data <= opts['max'])
        #
        good[mask] = 1
        return(good)
    
    @classmethod
    def aic_spike_test(clf, meta, data, **opts):
        """
        Execute spike test using an estimate of Aikake Information Criterion.
        
        This methods requires the last 4 points prior to the first point to test.
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
    def bioargo_spike_test(clf, meta, data, **opts):
        """
        Spike test according to BIO ARGO
        
        Options:
          p10_min: factor for minimum 10 percentile median difference
          p10_max: factor for maximum 10 percentile median difference
          p90_min: factor for minimum 90 percentile median difference
          p90_max: factor for maximum 90 percentile median difference
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
    def argo_spike_test(clf, meta, data, **opts):
        """
        Spike test according to MyOcean for T and S parameters
        
        Options:
          threshold: threshold for consecutive double 3-values differences
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
    def argo_gradient_test(clf, meta, data, **opts):
        """
        Gradient test according to BIO ARGO
        
        Options:
          threshold: threshold for consecutive 3-values difference
        """
        good = np.ones(len(data), dtype=np.int8)
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
    def frozen_profile_test(clf, meta, data, **opts):
        """
        Test for frozen profiles.
        
        In this case, data is a tuple with (depth, data) where depth and data are vectors of the same length. Note
        that this tests flags the whole profile.
        
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
    
    @classmethod    
    def trigger_test(clf, meta, data, **opts):
        """
        Test data against a trigger value. 
        
        The return value here is not a quality flag, but whether data is below (-1), equal (0) or 
        above (1) trigger value. The flag itself has to be implemented by the calling function.
        
        Options:
          treshold: threshold value
        """
        good = np.zeros(len(data), dtype=np.int8)
        mask = (data < opts['threshold'])
        good[mask] = -1
        mask = (data > opts['threshold'])
        good[mask] = 1
        return(good)
    
    @classmethod
    def missing_value_test(clf, meta, data, **opts):
        """
        Test data for a specific value defined for missing data.
        
        Options:
          nan: value used for missing data
        """
        good = np.ones(len(data), dtype=np.int8)
        mask = (data == opts['nan'])
        good[mask] = -1
        return(good)
    
    @classmethod    
    def sensor_comparison_test(clf, meta, data, **opts):
        """
        Check whether two sensors measuring the same parameter provide a similar value.
        
        Argument data is a tuple (s1, s2) with measurement vectors from sensor 1 and sensor 2 respectively.
         
        Options:
          threshold: maximum difference allowed
        """
        good = np.ones(data.shape[0], dtype=np.int8)
        diff = np.abs(data[1]-data[0])
        mask = (diff > opts['threshold'])
        good[mask] = -1
        return(good)
    
    @classmethod
    def sensor_relationship_test(clf, meta, data, **opts):
        """
        Check if the relationship between related parameters is within a certain value.
        
        Argument data is a tuple (p1, p2) with vectors of measurements from parameter 1 and 
        parameter 2 respectively.
        
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
    
       
COMMON_TESTS = {

    '*': [ 
        ('FROZEN_VALUE', QCTests.frozen_test, {}), 
        ],
    'TEMPERATURE': [ 
        ('GLOBAL_RANGE' , QCTests.range_test, { 'min': -2.5, 'max': 40.0 }),
        #('MEDSEA_RANGE' , QCTests.range_test, { 'min': 10.0, 'max': 40.0, 'area': Areas.MedSea         }),
        #('NWSHELF_RANGE', QCTests.range_test, { 'min': -2.0, 'max': 24.0, 'area': Areas.NorthWestShelf }),
        #('ARCTIC_RANGE' , QCTests.range_test, { 'min': -1.9, 'max': 25.0, 'area': Areas.Arctic         }),
        ],
    'SALINITY': [
        ('GLOBAL_RANGE', QCTests.range_test , { 'min':  2.0, 'max': 41.0 }),
        #('MEDSEA_RANGE' , QCTests.range_test, { 'min':  2.0, 'max': 40.0, 'area': Areas.MedSea         }),
        #('NWSHELF_RANGE', QCTests.range_test, { 'min':  0.0, 'max': 37.0, 'area': Areas.NorthWestShelf }),
        #('ARCTIC_RANGE' , QCTests.range_test, { 'min':  2.0, 'max': 40.0, 'area': Areas.Arctic         }),
        ],
    }
        