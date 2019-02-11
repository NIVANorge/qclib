"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

Provides package access to Global variables

(C) 14. jan. 2016 Pierre Jaccard
"""
   
class Areas:

    Baltic = {
        'lat': (53.5, 62.0, 66.0, 66.0, 53.5), 
        'lon': (10.0, 10.0, 20.0, 30.0, 30.0)
        }
    NW_Shelf = {
        'lat': ( 48,  68, 68, 48),
        'lon': (-30, -30, 15, 15) 
        }
    NorthSea = {
        'lat': (51, 60.0, 60., 51.), 
        'lon': (-3., -3., 10, 10)
        }         
    Arctic = {
        'lat': (  67,   89,  89,  67), 
        'lon': (-180, -180, 180, 180)
        }
    Iberic = {
        'lat': ( 30.0,  48.0, 48.0, 42.0, 40.0, 30.0),   
        'lon': (-30.0, -30.0,  0.0,  0.0, -5.5, -5.5)
        }
    MedSea = {
        'lat': (30.0, 40.0, 46.0, 46.0, 40.25, 40.25, 30.0), 
        'lon': (-5.5, -5.5,  5.0, 20.0, 26.60, 36.50, 36.5)
        }
    BlackSea = {
        'lat': (40.0, 40, 48, 48.0), 
        'lon': (26.5, 42, 42, 26.5)
        }
    Biscay = {
        'lat': (42,  48, 48,  42),  
        'lon': (-9,  -9,  0,   0)  
        }
    WesternGulfFinland = {
        'lat': (59.45, 59.45, 60.30, 60.30),
        'lon': (23.22, 30.20, 30.20, 23.22)
        }
    SouthernBalticProper = {
        'lat': (54.52, 54.52, 56.20, 56.20),
        'lon': (12.27, 17.09, 17.09, 12.27)
        }
    NorthernBalticProper = {
        'lat': (58.36, 58.36, 59.62, 59.62),
        'lon': (19.88, 23.21, 23.21, 19.88)
        }   


class Global_Threshold_Ranges: 
    '''
    from 
    http://archimer.ifremer.fr/doc/00251/36232/
    '''    
    Temperature =  { 'min': -2.5, 'max': 40.0 }
    Salinity =     { 'min':  2.0, 'max': 41.0 }
    Fluorescence = { 'min': -0.1, 'max': 80.0 }
    Oxygen  =      { 'min':  0.0, 'max': 500.0 } # Micromoles per liter!
    #Chlorophyll = {'min': -0.1, 'max': 80.0 } #Using Fluorescence method CPHL
    Temperature_Ferrybox = { 'min': -2.5, 'max': 100.0 }
    
class Local_Threshold_Ranges: 
    '''
    from 
    http://archimer.ifremer.fr/doc/00251/36232/
    '''
    all_months = [1,2,3,4,5,6,7,8,9,10,11,12] 
        
    Fluorescence =[ 
                  {'min': -0.1, 'max': 2.0,  'area': Areas.Arctic ,'months': [1,2,10,11,12]},
                  {'min': -0.1, 'max': 12.0, 'area': Areas.Arctic ,'months': [3,4] },  
                  {'min': -0.1, 'max': 6.0,  'area': Areas.Arctic ,'months': [5,6,7,8,9]},
                  
                  {'min': -0.1, 'max': 14.0, 'area': Areas.NorthSea,'months': [1,2,3,4,5,6]},
                  {'min': -0.1, 'max': 8.0,  'area': Areas.NorthSea,'months': [7,8]},    
                  {'min': -0.1, 'max': 12.0, 'area': Areas.NorthSea,'months': [9,10,11,12]},
                  
                  {'min': 0.5, 'max': 25.0, 'area': Areas.Baltic,'months': [1,2,11,11,12]},
                  {'min': 1.5, 'max': 77.6, 'area': Areas.Baltic,'months': [3,4,5]},
                  {'min': 0.5, 'max': 36.8, 'area': Areas.Baltic,'months': [6,7,8,9]},
                  
                  {'min': -0.1, 'max': 20.0, 'area': Areas.NW_Shelf, 
                   'months': [1,2,3,4,5,6,7,8,9]},
                  {'min': -0.1, 'max': 20.0, 'area': Areas.NW_Shelf, 
                   'months': [10,11,12] }                  
                  ]
     
    Oxygen =    [ 
                  {'min': 200.0, 'max': 500.0, 'area': Areas.Arctic ,'months': all_months},
                  {'min': 200.0, 'max': 500.0, 'area': Areas.NorthSea ,'months': all_months},  
                  {'min': 200.0, 'max': 500.0, 'area': Areas.Baltic ,'months': all_months},
                  {'min': 200.0, 'max': 500.0, 'area': Areas.NW_Shelf ,'months': all_months},                   
                ]



    