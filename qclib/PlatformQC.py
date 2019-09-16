import numpy as np
from typing import Dict, List
from .QCTests import QCTests
from .utils import Thresholds
from .utils.qc_input import QCInput
import copy

common_tests = {

    '*':
        {'frozen_test': [QCTests.frozen_test, {}],
         'missing_value_test': [QCTests.missing_value_test, {'nan': -999}]},
    'depth':
        {'flatness_test': [QCTests.flatness_test, {'max_variance': Thresholds.flatness_max_variance}]},
    'temperature':
        {'global_range_test': [QCTests.range_test,
                               Thresholds.global_range_temperature],
         'local_range_test': [QCTests.range_test,
                              Thresholds.local_range_temperature],
         'argo_spike_test': [QCTests.argo_spike_test,
                             {'spike_threshold': Thresholds.spike_thresholds['temperature']}
                             ]},
    'salinity':
        {'global_range_test': [QCTests.range_test,
                               Thresholds.global_range_salinity],
         'local_range_test': [QCTests.range_test,
                              Thresholds.local_range_salinity],
         'argo_spike_test': [QCTests.argo_spike_test,
                             {'spike_threshold': Thresholds.spike_thresholds['salinity']}
                             ]},

    'chla_fluorescence':
        {'global_range_test': [QCTests.range_test,
                               Thresholds.global_range_chla_fluorescence],
         'local_range_test': [QCTests.range_test,
                              Thresholds.local_range_chla_fluorescence]},

    'oxygen_concentration':
        {'global_range_test': [QCTests.range_test,
                               Thresholds.global_range_oxygen],
         'local_range_test': [QCTests.range_test,
                              Thresholds.local_range_oxygen],
         'argo_spike_test': [QCTests.argo_spike_test,
                             {'spike_threshold': Thresholds.spike_thresholds['oxygen']}]}

}


class PlatformQC(QCTests):
    sampling_interval = 60
    accept_time_difference = 3

    def __init__(self):
        self.qc_tests = copy.deepcopy(common_tests)
        for key in self.qc_tests.keys():
            if key != "*":
                self.qc_tests[key].update(self.qc_tests['*'])

    @staticmethod
    def get_combined_flag(flags: List[List[int]]) -> np.ndarray:
        transposed_flags = np.array(flags).T
        flag_0 = np.all(transposed_flags == 0, axis=1)
        flag_1 = np.any(transposed_flags == -1, axis=1)
        combined_flag = np.ones(len(transposed_flags), dtype=np.int)
        combined_flag[flag_1] = -1
        combined_flag[flag_0] = 0
        return combined_flag.tolist()

    def applyQC(self, data: QCInput, tests: Dict[str, List[str]]) -> Dict[str, List[int]]:
        """
        """
        flags = {}
        key = list(tests.keys())[0]
        if key not in self.qc_tests:
            key = "*"

        for test in self.qc_tests[key]:
            if test not in tests[list(tests.keys())[0]]:
                continue
            if type(self.qc_tests[key][test][1]) is list:  # only local range test
                arr = [[test, self.qc_tests[key][test][0], x] for x in self.qc_tests[key][test][1]]
                flag = []
                for n, a in enumerate(arr):
                    flag.append(a[1](data, **a[2]))
                flags[test] = self.get_combined_flag(flag)
            else:
                flags[test] = self.qc_tests[key][test][0](data, **self.qc_tests[key][test][1])
        return flags

    @staticmethod
    def get_overall_flag(flags: Dict[str, List[int]], *extra_flags) -> List[int]:
        # check if None values appear consistently for all flags for a given measurement
        flags_list = list(flags.values())
        flags_list_T = np.array(flags_list).T
        flag_None = np.any(flags_list_T == None, axis=1)
        assert all(flag_None == np.all(flags_list_T == None, axis=1))
        # I'm not sure if extra_flags is None or a tuple with None in it
        # check if flags and extra flags are equal length
        if extra_flags not in [None, (None,)]:
            for flags in extra_flags:
                assert len(flags) == len(flags_list[0])
                flags_list.append(flags)
        flags_list_T = np.array(flags_list).T
        flag_0 = np.any(flags_list_T == 0, axis=1)
        flag_1 = np.any(flags_list_T == -1, axis=1)
        flag_None = np.any(flags_list_T == None, axis=1)
        overall_flag = np.ones(len(flags_list_T))
        overall_flag[flag_0] = 0
        overall_flag[flag_1] = -1
        overall_flag[flag_None] = None
        final_flag = [flag if flag in [-1, 0, 1] else None for flag in overall_flag.tolist()]
        return final_flag

    @classmethod
    def flag2copernicus(cls, flag: List[int]) -> List[int]:
        " This function translates between -1,0,1 convention to copernicus convention 0,1,4 "
        return [fl if fl != -1 else 4 for fl in flag]
