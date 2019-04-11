#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import PlatformQC


class FerryboxQC(PlatformQC.PlatformQC):

    def __init__(self):
        super().__init__()
        extra_tests = {}
        # This is how to overwrite thresholds
        # self.qc_tests['temperature']["GLOBAL_RANGE"][1]=Thresholds.Global_Threshold_Ranges.Temperature_Ferrybox
        # And extra tests can be added
        self.qc_tests.update(extra_tests)


class SailBuoyQC(PlatformQC.PlatformQC):
    sampling_interval = 9000
    accept_time_difference = sampling_interval


class SeaGliderQC(PlatformQC.PlatformQC):
    pass


class WaveGliderQC(PlatformQC.PlatformQC):
    sampling_interval = 3600
    accept_time_difference = sampling_interval
