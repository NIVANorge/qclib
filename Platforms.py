#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Common


class FerryboxQC(Common.PlatformQC):
    
    # values for threshold should be checked and changed 
    
    QC_TESTS = {
    # 'TEMPERATURE': ['SPIKE_TEST' , QCTests.argo_spike_test, {'threshold': 4}],
    # 'SALINITY': ['SPIKE_TEST' , QCTests.argo_spike_test, {'threshold':2 }],
    }
     
    def QC(self,df,tests):
        flags = self.applyQC(df, tests)
        return flags
    
    def cmems(self,flags):       
        codes, overall_flags = self.CMEMScodes(flags)
        return codes,overall_flags


class SailBuoyQC(Common.PlatformQC):
    QC_TESTS = {}

    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        return flags

    def cmems(self, flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes, overall_flags


class SeaGliderQC(Common.PlatformQC):
    QC_TESTS = {}

    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        return flags

    def cmems(self, flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes, overall_flags


class WaveGliderQC(Common.PlatformQC):
    QC_TESTS = {}

    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        return flags

    def cmems(self, flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes, overall_flags