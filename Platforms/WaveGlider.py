'''
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Platforms.WaveGlider
============================
Specific tools for WaveGlider

Created on 14. feb. 2018
'''

from  pyFerry.Platforms import Common 

class WaveGliderQC(Common.PlatformQC):
    
    QC_TESTS = {}
    
    def QC(self, meta, data):
        flags = self.applyQC(meta, data)       
        return flags
    
    def cmems(self,flags):
        codes, overall_flags = self.CMEMScodes(flags)
        return codes,overall_flags    