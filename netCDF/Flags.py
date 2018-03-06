"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.netCDF.Flags
===========================



(C) 12. okt. 2016 Pierre Jaccard
"""

from .. import Loggers

from .Generic import Flags
from .. import QC
from .Data import RawFerrybox

log = Loggers.getLogger(__name__)

class RTQC_FLAGS(Flags):
    _CONTEXT_NODE = 'raw/ferrybox'
    _GROUP_NAME   = 'RTQC'
            
class RTQC_SHIP_SPEED_TEST(QC.QCTests):
    
    _FLAGS_GROUP   = RTQC_FLAGS
    _SUBSET_NAME   = 'NAVIGATION'
    _DIMENSIONS    = ('d_time',)
    _DESCRIPTION   = 'Bad if ship speed is less than 1m/s or larger than 20m/s'
    _VARIABLE_NAME = 'SHIP_SPEED'
    
    def qc(self, vmin=1.0, vmax=20.0):
        fb   = RawFerrybox(self._nc)
        self.range_test(fb.SHIP_SPEED, vmin, vmax)
        return

class RTQC_SHIP_SPEED_FROZEN_TEST(QC.QCTests):
    
    _FLAGS_GROUP   = RTQC_FLAGS
    _SUBSET_NAME   = 'NAVIGATION'
    _DIMENSIONS    = ('d_time',)
    _DESCRIPTION   = 'Bad if ship speed is frozen'
    _VARIABLE_NAME = 'SHIP_SPEED'
    
    def qc(self):
        fb  = RawFerrybox(self._nc)
        self.frozen_test(fb.SHIP_SPEED)
        return

class RTQC_PUMP_TEST(QC.QCTests):
    
    _FLAGS_GROUP   = RTQC_FLAGS
    _SUBSET_NAME   = 'SYSTEM'
    _DIMENSIONS    = ('d_time',)
    _DESCRIPTION   = 'Bad if pump is not running'
    _VARIABLE_NAME = 'PUMP'
    
    def qc(self):
        fb  = RawFerrybox(self._nc)
        self.range_test(fb.PUMP, 0.8, 1.2)
        return

class RTQC_OBSTRUCTION_TEST(QC.QCTests):
    
    _FLAGS_GROUP   = RTQC_FLAGS
    _SUBSET_NAME   = 'SYSTEM'
    _DIMENSIONS    = ('d_time',)
    _DESCRIPTION   = 'Bad if obstruction is triggered'
    _VARIABLE_NAME = 'OBSTRUCTION'
    
    def qc(self):
        fb  = RawFerrybox(self._nc)
        self.range_test(fb.OBSTRUCTION, None, 0.2)
        return

class RTQC_PUMP_HISTORY_TEST(QC.QCTests):
    
    _FLAGS_GROUP   = RTQC_FLAGS
    _SUBSET_NAME   = 'SYSTEM'
    _DIMENSIONS    = ('d_time',)
    _DESCRIPTION   = 'Bad if pump is has not been running for more than 5min'
    _VARIABLE_NAME = 'PUMP'
    
    def qc(self, dtmin=300):
        fb  = RawFerrybox(self._nc)
        self.history_test(fb.PUMP, 0.8, 1.2, fb.time, dtmin)
        return

class RTQC_OBSTRUCTION_HISTORY_TEST(QC.QCTests):
    
    _FLAGS_GROUP   = RTQC_FLAGS
    _SUBSET_NAME   = 'SYSTEM'
    _DIMENSIONS    = ('d_time',)
    _DESCRIPTION   = 'Bad if obstruction was triggered less than 5min earlier'
    _VARIABLE_NAME = 'OBSTRUCTION'
    
    def qc(self, dtmin=300):
        fb  = RawFerrybox(self._nc)
        self.history_test(fb.OBSTRUCTION, None, 0.2, fb.time, dtmin)
        return

class RTQC_TEMPERATURE_TESTS(QC.MultiVarQCTests):

    def __init__(self, ncfile):
        super(RTQC_TEMPERATURE_TESTS, self).__init__(ncfile, 'TEMPERATURE', RTQC_FLAGS)
        return
    
    def qc(self, Tmin, Tmax):
        self.frozen_test()
        self.range_test(Tmin, Tmax, flag_name='{_var_}_GLOBAL_RANGE_TEST')
        return
    
class RTQC_SALINITY_TESTS(QC.MultiVarQCTests):

    def __init__(self, ncfile):
        super(RTQC_SALINITY_TESTS, self).__init__(ncfile, 'SALINITY', RTQC_FLAGS)
        return
    
    def qc(self):
        self.frozen_test()
        return

class RTQC_CHLA_FLUORESCENCE_TESTS(QC.MultiVarQCTests):

    def __init__(self, ncfile):
        super(RTQC_CHLA_FLUORESCENCE_TESTS, self).__init__(ncfile, 'CHLA_FLUORESCENCE', RTQC_FLAGS)
        return
    
    def qc(self):
        self.frozen_test()
        return
        
class RTQC_CDOM_FLUORESCENCE_TESTS(QC.MultiVarQCTests):

    def __init__(self, ncfile):
        super(RTQC_CDOM_FLUORESCENCE_TESTS, self).__init__(ncfile, 'CDOM_FLUORESCENCE', RTQC_FLAGS)
        return
    
    def qc(self):
        self.frozen_test()
        return

class RTQC_TURBIDITY_TESTS(QC.MultiVarQCTests):

    def __init__(self, ncfile):
        super(RTQC_TURBIDITY_TESTS, self).__init__(ncfile, 'TURBIDITY', RTQC_FLAGS)
        return
    
    def qc(self):
        self.frozen_test()
        return
