import json
import pandas as pd
import requests as rq
import bz2, os   
import datetime 
from datetime import datetime as dt
import numpy as np

from  pyFerry.Platforms import TestGlider 
from  pyFerry.Platforms import Ferrybox
from  pyFerry.Platforms import WaveGlider
from  pyFerry.Platforms import SeaGlider
from  pyFerry.Platforms import SailBuoy

# all parameter name are corrected to lowercase 
params_dict =  {'ctd_temperature':'temperature',
                'oxygen_temp':'temperature',
                'ctd_salinity':'salinity',
                'oxygen_concentration':'oxygen_concentration',
                'turbidity':'turbidity',
                'chla_fluorescence':'fluorescence'
                }  


platforms = {'MS Trollfjord': Ferrybox.FerryboxQC,
            'FA': Ferrybox.FerryboxQC,
            'SG644': SeaGlider.SeaGliderQC,
            'SB1709D2': SailBuoy.SailBuoyQC,
            'SV3-154': WaveGlider.WaveGliderQC
             } 

varnames_dict = {'FA': ('CTD_SALINITY','CTD_TEMPERATURE','OXYGEN_CONCENTRATION','CHLA_FLUORESCENCE','TURBIDITY')
    }
 
def get_name_lookup(PLATFORM_PATH):

    '''
    Example code on how to query 
    meta structure for a platform/vessel
    and also create a dictionary with all 
    the time series elements
   
    to port forward from gcloud:
    
    gcloud container clusters get-credentials k8s-dev    
    check pods: 
    
    kubectl get pods  
    for metadata : 
    
    kubectl port-forward <name_of_pod_with_metaflow-...> 4000:5000
    '''

    def _walk_tree(top):
        
        """walk a tree of parts and yield all time series objects"""
        
        if top.get("parts", False) and len(top["parts"]) > 0:
            for t in top["parts"]:
                for ct in _walk_tree(t):
                    yield ct
        if top.get("ttype") in ["tseries", "qctseries", "gpstrack"]:
            yield top
        
    # Get "root" meta data for platform
    META_SOURCE = "http://127.0.0.1:4000"
    par = {"path": PLATFORM_PATH, "unique": True}
    r = rq.get(META_SOURCE, params=par)
    in_data = r.json()
    assert("t" in in_data)
    platform = in_data["t"]
    
    # Get full tree for platform
    par = {"uuid": platform["uuid"], "parts": 100}
    r = rq.get(META_SOURCE, params=par)
    platform_tree = r.json()["t"]
    
    # Get list of all time series objects
    ts_list = [ts for ts in _walk_tree(platform_tree)]
   
    # Create lookup dictionary for the time series
    name_lookup = {ts["name"]: ts for ts in ts_list if "name" in ts}
    return name_lookup

       
def read_files(path): 
    
    '''reads all json files from given folder,
       combines into one dataframe '''
    
    files_all = os.listdir(path)
    files = [i for i in files_all if i.endswith('.json.bz2')]
    
    # read 1st file with t to get platform name 
    for f in files:                
            d =  bz2.BZ2File(os.path.join(path,f),'rb')
            d = d.read()
            d = json.loads(d)
            if ("t" in d):
                # path not ship code 
                platform = d['t'][0]['SHIP_CODE']
                break

    
    # read files, create dictionary of data    
    data_df = {'SHIP_CODE':[],'TIME':[],
                 'GPS_LATITUDE':[],'GPS_LONGITUDE':[]}     
   
    varnames = varnames_dict[platform]   
    
    for name in varnames: 
        data_df.update({name:[]})    

    for f in files:                
        d =  bz2.BZ2File(os.path.join(path,f),'rb')
        d = d.read()
        d = json.loads(d)
        if ("t" in d):
            arr = d['t']
            for m in range(0,len(arr)):
                pl = arr[m]['SHIP_CODE']
                
                t = dt.strptime(arr[m]['SYSTEM_DATE_DMY']+arr[m]['SYSTEM_TIME'],'%d.%m.%Y%H:%M:%S')
                time = t.strftime('%Y-%m-%dT%H:%M:%S')

                data_df['SHIP_CODE'].append(pl)
                data_df['TIME'].append(time)
                data_df['GPS_LATITUDE'].append(float(arr[m]['GPS_LATITUDE']))
                data_df['GPS_LONGITUDE'].append(float(arr[m]['GPS_LONGITUDE']))     

                # to add smth generic iterating through 
                # variables in json file    
                for name in varnames: 
                    var = float(arr[m][name])
                    data_df[name].append(var)
                
    data_df =  pd.DataFrame(data = data_df)        
    return data_df 
                
def get_metadata(data_df): 
    
    ''' creates dataframe with metadata 
        for given platform '''
    
    # check all ship codes are the same  
    assert len(set(data_df['SHIP_CODE']))== 1
    platform = data_df['SHIP_CODE'][0]         
    name_lookup = get_name_lookup(platform)
    metadata_df = {'signal_list':[]}
    for name in data_df.keys():
        if name in ('TIME','SHIP_CODE','GPS_LATITUDE','GPS_LONGITUDE'):
            continue
        else: 
            param = params_dict[name.lower()]
            match_meta = name_lookup[name.lower()]
            match_meta['parameter_type'] = param.upper()

            metadata_df['lat'] = data_df['GPS_LATITUDE']
            metadata_df['lon'] = data_df['GPS_LONGITUDE']
            metadata_df[name] = match_meta
            metadata_df['signal_list'].append(name)
            metadata_df['platform'] = platform  
 
    metadata_lists = metadata_df.copy()    
    for k,v in metadata_df.items(): 
        if isinstance(metadata_lists[k],(np.ndarray,pd.Series)):  
            metadata_lists[k] = metadata_df[k].tolist()
        
    return metadata_df,metadata_lists     
   
def final_dict(qc,data_df):
    
    ''' function combines data,
        flags and codes 
        into json file '''   
    
    flags = json.loads(json.dumps(qc[0])) 
    codes = json.loads(json.dumps(qc[1]))
    ov_flags = json.loads(json.dumps(qc[2]))
    
    # add codes to table data
    for k, v in codes.items():
        data_df["CODE_%s" % (k,)] = v

    # add codes to table data
    for k, v in ov_flags.items():
        data_df["OVERALL_FLAG_%s" % (k,)] = v
        
    # add flags to table data
    for k, v in flags.items():
        for f, fa in v.items():
            data_df["FLAG_%s_%s" % (k, f)] = fa



    # transform to list of dictionaries
    list_of_records = data_df.to_dict(orient='records')       
    # serialize in json format
    out_dict = {"t": list_of_records} 
    
    return out_dict        

def write_to_file(path,out_dict,move_raw =False):
    
    ''' writes final data+qc to json file ''' 
    
    p = os.path.join(path,'processed')       
    if not os.path.exists(p):
        os.mkdir(p)
    with open(os.path.join(p,"table_records.json"), "w") as f:
        json.dump(out_dict, f, indent=4)        

    if move_raw == True: 
        # move all raw files to another directory        
        files_all = os.listdir(path)
        files = [i for i in files_all if i.endswith('.json.bz2')]
        for f in files: 
            os.rename(path, p)        
                             
def call_QC(meta,data):
    
    ''' calls QC modules for this platform'''    
    

    
    x = platforms[meta['platform']]()
    flags = x.QC(meta,data)
    codes,overall_flags = x.cmems(flags)
    #flags = flags.append(overall_flags)
    return (flags,codes,overall_flags)

if __name__ == '__main__': 
    
    test = 'Ferrybox'
       
    if test == 'Ferrybox':
        '''    
        data from the cloud
        ferrybox01:FERRYDATA/incoming/RT/NIVA/FA/*.json.bz2   
        '''    
        # 1 specify files location 
        path = r'C:\Users\elp\OneDrive\ferrybox\FERRYDATA\cloud' 
        
        # 2 open files, unzip, read variables according to platform 
        data_df = read_files(path)  
        
        # save data to separate file   
        # data_df.to_csv('data_df.csv')  
         
        # 4 get metadata for these variables     
        metadata_df,metadata_list = get_metadata(data_df)  
        
        # save metadata to separate json file  
        # with open('metadata_ferrybox.json','w') as f: 
        #    json.dump(metadata_list,f,indent=4) 
            
        # 5 send to qc        
        x = call_QC(metadata_df,data_df)
        
        # 6 make json with data,flags and codes 
        out_dict = final_dict(x,data_df) 
        
        # 7 if needed, write output array to file 
        write_to_file(path,out_dict) 
        