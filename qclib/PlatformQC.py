'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>

========================
Common classes and tools for platforms

Created on 14. feb. 2018
'''
import numpy as np
from typing import Dict
from .QCTests import QCTests
from .utils import Thresholds
from .utils.qc_input import QCInput_df
import itertools
import copy

# '''
# In the document 
# http://archimer.ifremer.fr/doc/00251/36232/
# the ranges are defined for different depths 
# For now the ranges defined here only for the surface
# '''
common_tests = {

    '*':
        {'frozen_test': [QCTests.rt_frozen_test, {}],
         'missing_value_test': [QCTests.rt_missing_value_test, {'nan': -999}
                                ]},
    'temperature':
        {'global_range_test': [QCTests.rt_range_test,
                               Thresholds.global_range_temperature],
         'local_range_test': [QCTests.rt_range_test,
                              Thresholds.local_range_temperature],
         'argo_spike_test': [QCTests.argo_spike_test,
        {'spike_threshold': Thresholds.spike_thresholds['temperature']}
                             ]},
    'salinity':
        {'global_range_test': [QCTests.rt_range_test,
                               Thresholds.global_range_salinity],
         'local_range_test': [QCTests.rt_range_test,
                              Thresholds.local_range_oxygen],
         'argo_spike_test': [QCTests.argo_spike_test,
        {'spike_threshold': Thresholds.spike_thresholds['salinity']}
                             ]},

    'chla_fluorescence':
        {'global_range_test': [QCTests.rt_range_test,
                               Thresholds.global_range_chla_fluorescence],
         'local_range_test': [QCTests.rt_range_test,
                              Thresholds.local_range_chla_fluorescence]},

    'oxygen_concentration':
        {'global_range_test': [QCTests.rt_range_test,
                               Thresholds.global_range_oxygen],
         'local_range_test': [QCTests.rt_range_test,
                              Thresholds.local_range_oxygen],
         'argo_spike_test': [QCTests.argo_spike_test,
        {'spike_threshold': Thresholds.spike_thresholds['oxygen']}]}
        
        }


class PlatformQC(QCTests):

    def __init__(self):
        self.qc_tests = copy.deepcopy(common_tests)


    def applyQC(self, qcinput: QCInput_df, tests: Dict[str, str]) -> Dict[str, int]:
        """
      df : dataframe wih col: datetime, name (platform code), lon, lat, data
         where data is e.g. salinity or temperature, or fdom, etc.,..
     tests : dictionary with key being name (e.g. temperature, or salinity, or...)
      and with value being a list of tests =["global_range","local_range"]...
        """
        flags = {}
        key = list(tests.keys())[0]
        if key in ['temperature', 'oxygen_concentration', 'fluorescence', 'salinity']:
            self.qc_tests[key].update(self.qc_tests['*'])

        for test in tests[key]:
            if key not in self.qc_tests:
                key = "*"

            if type(self.qc_tests[key][test][1]) is list:  # only range test
                arr = [[test, self.qc_tests[key][test][0], x] for x in self.qc_tests[key][test][1]]
                flag = []
                for n, a in enumerate(arr):
                    flag.append(a[1](qcinput, **a[2]))

                if all([flg == 0 for flg in flag]):
                    combined_flag = 0
                elif any([flg == -1 for flg in flag]):
                    combined_flag = -1
                else:
                    combined_flag = 1

                flags[test] = combined_flag
            else:
                flag = self.qc_tests[key][test][0](qcinput, **self.qc_tests[key][test][1])
                if test not in flags:
                    flags[test] = flag

        return flags

    @classmethod
    def rt_get_overall_flag(cls, flags: Dict) -> int:

        overall_flag = 1
        if all([flg == 0 for flg in flags.values()]):
            overall_flag = 0
        for flg in flags.values():
            if flg == -1:
                overall_flag = -1

        return overall_flag

