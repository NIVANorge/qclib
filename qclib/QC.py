from typing import Dict, List
from .PlatformQC import PlatformQC
from .utils.qc_input import QCInput
from .utils.qc_input_helpers import remove_nans, flags_resized_to_include_values_for_nan
from .utils.validate_input import assert_is_sorted
from . import Platforms
import logging

# NOTE: when a new platform is added it has to be added to the array below, with "new_platform": Common.PlatformQC
platform_dict = {'TF': Platforms.FerryboxQC,
                 'FA': Platforms.FerryboxQC,
                 'NB': Platforms.FerryboxQC,
                 'Survey_2018_03/SeaGlider_1':  Platforms.SeaGliderQC,
                 'Survey_2019_04/SeaGlider_1':  Platforms.SeaGliderQC,
                 'Survey_2019_04_test/SeaGlider_1':  Platforms.SeaGliderQC,
                 'Survey_2018_03/SB_Echo':      Platforms.SailBuoyQC,
                 'Survey_2019_04/SB_Echo':      Platforms.SailBuoyQC,
                 'Survey_2019_04_test/SB_Echo':      Platforms.SailBuoyQC,
                 'Survey_2018_03/Waveglider_1': Platforms.WaveGliderQC,
                 'Survey_2019_04/Waveglider_1': Platforms.WaveGliderQC,
                 'Survey_2019_test/Waveglider_1': Platforms.WaveGliderQC}


def init(name):
    if name not in platform_dict:
        return PlatformQC()
    else:
        return platform_dict[name]()


def execute(obj, data: QCInput, tests: Dict[str, Dict[str, bool]]) -> Dict[str, List[int]]:
    assert_is_sorted(data)
    data_without_nan_values = remove_nans(data)
    if data_without_nan_values.values:
        flags = obj.applyQC(data_without_nan_values, tests)
    else:
        flags = {test: [] for test in next(iter(tests.values())).keys()}
    if len(data.values) == len(data_without_nan_values.values):
        return flags
    elif len(data.values) > len(data_without_nan_values.values):
        return flags_resized_to_include_values_for_nan(flags, data)
    else:
        logging.error(f"inconsistent input data")


def finalize():
    print("Successfully run QC")
    pass

