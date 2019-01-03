#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PlatformQC
import Thresholds


class FerryboxQC(PlatformQC.PlatformQC):

    sampling_frequency = 60
    frequency_units = "seconds"

    def __init__(self):
        super().__init__()
        extra_tests = {}
        # This is how to overwrite thresholds
        # self.qc_tests['temperature']["GLOBAL_RANGE"][1]=Thresholds.Global_Threshold_Ranges.Temperature_Ferrybox
        # And extra tests can be added
        self.qc_tests.update(extra_tests)

class SailBuoyQC(PlatformQC.PlatformQC):
    pass

class SeaGliderQC(PlatformQC.PlatformQC):
    pass

class WaveGliderQC(PlatformQC.PlatformQC):
    pass
