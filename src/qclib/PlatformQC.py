import copy
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
import warnings

from qclib.QCTests import QCTests
from qclib.utils import Thresholds
from qclib.utils.qc_input import QCInput

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
                             {'spike_threshold': Thresholds.spike_thresholds['oxygen']}]},

    'pump':
        {'pump_history_test': [QCTests.pump_history_test, {}]},

    'velocity':
        {'global_range_test': [QCTests.range_test,
                               Thresholds.global_range_velocity_ferrybox],
         'bounded_variance_test': [QCTests.bounded_variance_test,
                                   {'max_variance': Thresholds.velocity_max_variance}]
         }
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
        combined_flag = np.ones(len(transposed_flags), dtype=int)
        combined_flag[flag_1] = -1
        combined_flag[flag_0] = 0
        return combined_flag.tolist()

    def applyQC(self, qc_input: QCInput, measurement_name: str, tests: List[str]) -> Dict[str, List[int]]:
        """
        """

        flags = {}
        if measurement_name not in self.qc_tests:
            logging.debug(f"'{measurement_name}' is not defined in qc_tests, using default tests instead")
            measurement_name = "*"

        for test in tests:
            if test not in self.qc_tests[measurement_name]:
                raise Exception(f"This test: '{test}' is not available for this measurement '{measurement_name}'")
            if type(self.qc_tests[measurement_name][test][1]) is list:  # only local range test
                arr = [[test, self.qc_tests[measurement_name][test][0], x] for x in
                       self.qc_tests[measurement_name][test][1]]
                flag = []
                for n, a in enumerate(arr):
                    flag.append(a[1](qc_input, **a[2]))
                flags[test] = self.get_combined_flag(flag)
            else:
                flags[test] = self.qc_tests[measurement_name][test][0](qc_input, **self.qc_tests[measurement_name][test][1])
        return flags

    @staticmethod
    def get_overall_flag(flags: Dict[str, List[int]], *extra_flag_lists: Optional[List[int]]) -> List[int]:
        """
        Current function calculates overall flags for the list of values for one parameter
        # Overall Flag can be calculated from different combinations of QC flags :
        # 1. flags related to the given variable + gsp flags + pump status flags
        # 2. gsp flags + pump status flags
        # 3. only gsp flags (for parameters not affected by pump status)
        """
        if not flags:
            # If flags dict is empty
            list_of_flags_lists: Union[List[Any], Any] = []
        else:
            list_of_flags_lists = list(flags.values())
            if len(list_of_flags_lists) > 0:
                verify_if_any_none_all_none(list_of_flags_lists)

        # TODO: add assert that at least one list with flags should be not empty
        for extra_flag_list in extra_flag_lists:
            if extra_flag_list is not None:
                list_of_flags_lists.append(extra_flag_list)

        list_of_flags_lists_T = np.array(list_of_flags_lists).T
        if list_of_flags_lists_T.ndim > 1:
            # flags_all_zeroes = np.all(list_of_flags_lists_T == 0, axis=1)
            flags_have_negative_one = np.any(list_of_flags_lists_T == -1, axis=1)
            logging.debug(f"'{flags_have_negative_one, list_of_flags_lists_T}' is not defined in qc_tests, using "
                          f"default tests instead")
            flags_have_nones = np.any(list_of_flags_lists_T == None, axis=1)

            overall_flag = np.ones(len(list_of_flags_lists_T))

            overall_flag[flags_have_negative_one] = -1
            overall_flag[flags_have_nones] = None

            final_flag = [flag if flag in [-1, 0, 1] else None for flag in overall_flag.tolist()]
        else:
            final_flag = list_of_flags_lists
        return final_flag

    @classmethod
    def flag2copernicus(cls, flag: List[int]) -> List[int]:
        " This function translates between -1,0,1 convention to copernicus convention 0,1,4 "
        return [fl if fl != -1 else 4 for fl in flag]


def verify_if_any_none_all_none(list_of_flags_lists: List[List[int]]):
    list_of_flags_lists_T = np.array(list_of_flags_lists).T
    flag_none = np.any(list_of_flags_lists_T == None, axis=1)
    if not all(flag_none == np.all(list_of_flags_lists_T == None, axis=1)):
        raise Exception('If there is any None in a flag array they should all be None')
