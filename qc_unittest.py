'''
Created on 15. jan. 2018
@author: ELP
'''
import unittest
import pandas as pd 


class FrozenTest(unittest.TestCase):
    a = {
       'CHLA_FLUORESCENCE' : [0.345, 10.0, 50,50],
       'CTD_SALINITY' : [ 25.700, 25.720, 77 , 77],
       'CTD_TEMPERATURE' : [14.024, 14.014, -20, -20],
       'GPS_LATITUDE' : [59.9091, 59.9091, 59.9091, 159.9091],
       'GPS_LONGITUDE' : [10.7057, 10.7077, 10.7087, 70.7087],
       'SHIP_CODE' : ['FA','FA','FA','FA']
        }
    df_a = pd.DataFrame(data=a)
    
    
    def test_frozen(self):
        ''' FrozenTest should add right flags'''
        #for var in (self.a,self.b):
        metadata_a,metadata_list = utils.get_metadata(self.df_a)          
        #test = qc.QC(df_a)
        flags,codes,overall_flagstest = utils.call_QC(metadata_a,self.df_a)
        df_flags = pd.DataFrame(data=flags)
        for key in self.df_a.keys():
            if key not in ['GPS_LATITUDE','GPS_LONGITUDE','SHIP_CODE']:
                self.assertEqual(flags[key]['FROZEN_VALUE'],[1, 1, 1,-1])


    def test_global_range(self):
        ''' GlobalRangeTest should add right flags'''
        metadata_a,metadata_list = utils.get_metadata(self.df_a)  
        flags,codes,overall_flagstest = utils.call_QC(metadata_a,self.df_a)       
        for key in self.df_a.keys(): 
            if key not in ['GPS_LATITUDE','GPS_LONGITUDE','CHLA_FLUORESCENCE','SHIP_CODE']:            
                self.assertEqual(flags[key]['GLOBAL_RANGE'],[1,1,-1,-1])

    

            
if __name__ == '__main__':
    unittest.main()