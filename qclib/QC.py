from typing import Dict, List
from .PlatformQC import PlatformQC
from .utils.qc_input import QCInput
from .utils.validate_input import is_sorted
from . import Platforms

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

    assert is_sorted(data), "Input data has to be sorted ascending in time"
    flags = obj.applyQC(data, tests)
    return flags


def finalize():
    print("Successfully run QC")
    pass

