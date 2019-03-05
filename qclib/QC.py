from typing import Dict
import pandas as pd
from .PlatformQC import PlatformQC
from .utils.qc_input import QCInput, QCInput_df
from . import Platforms
from .utils.measurement import measurement_list_to_dataframe
from .utils.validate_input import validate_additional_data
# NOTE: when a new platform is added it has to be added to the array below, with "new_platform": Common.PlatformQC
platform_dict = {'TF': Platforms.FerryboxQC,
                 'FA': Platforms.FerryboxQC,
                 'NB': Platforms.FerryboxQC,
                 'Survey_2018_03/SeaGlider_1':  Platforms.SeaGliderQC,
                 'Survey_2018_03/SB_Echo':      Platforms.SailBuoyQC,
                 'Survey_2018_03/Waveglider_1': Platforms.WaveGliderQC}


def init(name):
    if name not in platform_dict:
        return PlatformQC()
    else:
        return platform_dict[name]()


def execute(obj, qcinput: QCInput, tests: Dict[str, str])->Dict[str, int]:

    historical_values_df = measurement_list_to_dataframe(qcinput.historical_data)
    future_values_df = measurement_list_to_dataframe(qcinput.future_data)
    current_data_df = pd.DataFrame.from_dict({"data": [qcinput.value], "time": [qcinput.timestamp]})
    qcinput_df = QCInput_df(current_data=current_data_df, longitude=qcinput.longitude, latitude=qcinput.latitude,
                            historical_data=historical_values_df, future_data=future_values_df)

    validate_additional_data(qcinput_df)
    flags = obj.applyQC(qcinput_df, tests)
    return flags


def finalize():
    print("Successfully run QC")
    pass

