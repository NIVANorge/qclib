import logging
from typing import Dict, List

from qclib import Platforms
from qclib.PlatformQC import PlatformQC
from qclib.utils.qc_input import QCInput
from qclib.utils.qc_input_helpers import remove_nans, flags_resized_to_include_values_for_nan
from qclib.utils.validate_input import assert_is_sorted

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


def execute(platform: PlatformQC, qc_input: QCInput, measurement_name: str, tests: List[str]) -> Dict[str, List[int]]:
    assert_is_sorted(qc_input)
    qc_input_without_none_values = remove_nans(qc_input)
    if qc_input_without_none_values.values:
        flags = platform.applyQC(qc_input=qc_input_without_none_values, measurement_name=measurement_name, tests=tests)
    else:
        return {test: [None] * len(qc_input.values) for test in tests}
    if len(qc_input.values) == len(qc_input_without_none_values.values):
        return flags
    elif len(qc_input.values) > len(qc_input_without_none_values.values):
        return flags_resized_to_include_values_for_nan(flags, qc_input)
    else:
        logging.error(f"inconsistent input data")


def finalize():
    print("Successfully run QC")
    pass

