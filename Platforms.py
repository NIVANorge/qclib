#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PlatformQC


class FerryboxQC(PlatformQC.PlatformQC):

    # values for threshold should be checked and changed 
    
    QC_TESTS = {
    # 'TEMPERATURE': ['SPIKE_TEST' , QCTests.argo_spike_test, {'threshold': 4}],
    # 'SALINITY': ['SPIKE_TEST' , QCTests.argo_spike_test, {'threshold':2 }],
    }

    sampling_frequency = 60
    frequency_units = "seconds"

    def QC(self,df,tests):
        flags = self.applyQC(df, tests)
        return flags
    
    def cmems(self,flags):       
        codes, overall_flags = self.CMEMScodes(flags)
        return codes,overall_flags


class SailBuoyQC(PlatformQC.PlatformQC):
    QC_TESTS = {}

    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        return flags

    def cmems(self, flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes, overall_flags


class SeaGliderQC(PlatformQC.PlatformQC):
    QC_TESTS = {}

    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        return flags

    def cmems(self, flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes, overall_flags


class WaveGliderQC(PlatformQC.PlatformQC):
    QC_TESTS = {}

    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        return flags

    def cmems(self, flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes, overall_flags