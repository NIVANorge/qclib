#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from  pyFerry.Platforms import Common 
from pyFerry.QC import QCTests

class SeaGliderQC(Common.PlatformQC):
    
    QC_TESTS = {}
     
    def QC(self, meta, data):
        flags = self.applyQC(meta, data)       
        return flags
    
    def cmems(self,flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes,overall_flags
