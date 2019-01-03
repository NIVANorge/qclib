from PlatformQC import PlatformQC
import Platforms

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

def execute(obj, df, tests):
    
    flags = obj.applyQC(df,tests)
    obj.format_flags(flags)
    return flags

def finalize():
    print("Successfully run QC")
    pass
