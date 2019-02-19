'''
Created on 15. jan. 2018
@author: ELP
Temporary module for testing 
to be deleted later

'''
import unittest
import pandas as pd 
import qclib.QC
from qclib.utils.qc_input import QCInput
import qclib.utils.Thresholds 
import numpy as np
from datetime import datetime


platform_code = 'TF'
common_tests = qclib.QC.init(platform_code).qc_tests



f = '%Y-%m-%d %H:%M:%S'
now = datetime.strptime('2017-01-12 14:12:06', f)

frozen_historical_data = pd.DataFrame.from_dict(
    {"data": [12, 12, 12, 12],
     "time": [datetime.strptime('2017-01-12 14:08:06', f),
              datetime.strptime('2017-01-12 14:09:06', f),
              datetime.strptime('2017-01-12 14:10:06', f),
              datetime.strptime('2017-01-12 14:11:06', f)]})

spiky_historical_data = pd.DataFrame.from_dict(
        {"data": [3],
         "time": [datetime.strptime('2017-01-12 14:08:06', f)]})
spiky_historical_data = spiky_historical_data.set_index(["time"])

spiky_future_data = pd.DataFrame.from_dict({"data": [3], "time": datetime.strptime('2017-01-12 14:31:06', f) })
spiky_future_data = spiky_future_data.set_index(["time"])


spiky_data = QCInput(value=20, timestamp=now, historical_data = spiky_historical_data,future_data = spiky_future_data)

df = pd.DataFrame.from_dict({"data": [spiky_data.value], "time": [spiky_data.timestamp]})
df = df.set_index(['time'])



def merge_data(df, df_2, df_3):
    if df_2 is None:
        return df
    result = pd.concat([df, df_2,df_3])
    #result.set_index(["time"])
    sorted = result.sort_values(by="time", ascending=True)
    return sorted

data = merge_data(spiky_data.historical_data,df,spiky_data.future_data)

#df = df.set_index('time')
#spiky_data = spiky_data.set_index(["time"])
#print('spiky data\n', df)
print ('data',data)    
final_flag_is_plus_one = [0,0,1,0,0]
final_flag_is_minus_one = [0, 0, 1, 0, -1]
final_flag_is_zero = [0, 0, 0, 0, 0]


def test_argo_spike():
    measurement_name = 'temperature'
    params = common_tests[measurement_name]['argo_spike_test'][1]
    flag = common_tests[measurement_name]['argo_spike_test'][0](spiky_data,**params)
    print (flag)


#test_argo_spike()