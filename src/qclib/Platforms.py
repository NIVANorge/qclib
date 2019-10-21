#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from qclib import PlatformQC


class FerryboxQC(PlatformQC.PlatformQC):

    def __init__(self):
        super().__init__()
        extra_tests = {}
        # This is how to overwrite thresholds
        # self.qc_tests['temperature']["GLOBAL_RANGE"][1]=Thresholds.Global_Threshold_Ranges.Temperature_Ferrybox
        # And extra tests can be added
        self.qc_tests.update(extra_tests)

# Glider have in general unstable sampling interval.
# NUmber below are given as an upper limit for sampling interval and the accept_time difference
# is used to assess weather we had a gap in data taking or not.


class SailBuoyQC(PlatformQC.PlatformQC):
    sampling_interval = 9000
    accept_time_difference = sampling_interval


class SeaGliderQC(PlatformQC.PlatformQC):
    sampling_interval = 60
    accept_time_difference = 60*sampling_interval
    pass


class WaveGliderQC(PlatformQC.PlatformQC):
    sampling_interval = 3600
    accept_time_difference = sampling_interval
