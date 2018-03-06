'''
Created on 2. feb. 2018

@author: ELP
'''

from  pyFerry.Platforms import Common 



class TestQC(Common.PlatformQC):
    
    QC_TESTS = {}
    
    def QC(self, meta, data):
        flags = self.applyQC(meta, data)
        codes = self.CMEMScodes(flags)
        return(codes,flags)

