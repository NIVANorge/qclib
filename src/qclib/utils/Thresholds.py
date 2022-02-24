"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>
Provides package access to Global variables
(C) 14. jan. 2016 Pierre Jaccard, Elizaveta Protsenko

Source 1 = http://archimer.ifremer.fr/doc/00251/36232/ 
"""
# here Baltic polygone includes Skagerrak and Kattegat
# therefore, it may contain water masses from 
# the North Sea and corresponding TS
#TODO: split into subregiona, define ranges.  

Baltic = {'lat': (53.5, 62.0, 66.0, 66.0, 53.5),
          'lon': (10.0, 10.0, 20.0, 30.0, 30.0)}

NW_Shelf = {'lat': (50, 60, 60, 50),
            'lon': (-20, -20, 10.01, 10.01)}

SW_Shelf = {'lat': (25, 50, 50, 25),
            'lon': (-30, -30, 0, 0)}

NorthSea = {'lat': (51, 60.0, 60., 51.),
            'lon': (-3., -3., 10, 10)}

# This is a visualization of the arctic: https://drive.google.com/open?id=1rhhIpTLR7J06_6qzP3a3i1sbP6td_og5&usp=sharing
Arctic = {'lat': (89, 60,  60, 62, 66.0, 66.0, 60, 60, 89),
          'lon': (-180, -180, 10, 10, 20, 30, 30, 180, 180,)}

Iberic = {'lat': (30.0, 48.0, 48.0, 42.0, 40.0, 30.0),
          'lon': (-30.0, -30.0, 0.0, 0.0, -5.5, -5.5)}

MedSea = {'lat': (30.0, 40.0, 46.0, 46.0, 40.25, 40.25, 30.0),
          'lon': (-5.5, -5.5, 5.0, 20.0, 26.60, 36.50, 36.5)}

BlackSea = {'lat': (40.0, 40, 48, 48.0),
            'lon': (26.5, 42, 42, 26.5)}

Biscay = {'lat': (42, 48, 48, 42),
          'lon': (-9, -9, 0, 0)}

W_GulfFinland = {'lat': (59.45, 59.45, 60.30, 60.30),
                 'lon': (23.22, 30.20, 30.20, 23.22)}

S_BalticProper = {'lat': (54.52, 54.52, 56.20, 56.20),
                  'lon': (12.27, 17.09, 17.09, 12.27)}

N_BalticProper = {'lat': (58.36, 58.36, 59.62, 59.62),
                  'lon': (19.88, 23.21, 23.21, 19.88)}

# FIXME: Currently local_* thresholds is a list[Dict] while global_* and spike_*
#   is a Dict. This has consequences for as to how the flag is calculated in applyQC
# Global_Threshold_Ranges:
''' from Source 1 '''
global_range_temperature = {'min': -2.5, 'max': 40.0}
global_range_salinity = {'min': 2.0, 'max': 41.0}
global_range_chla_fluorescence = {'min': -0.5, 'max': 80.0}
global_range_oxygen = {'min': 0.0, 'max': 500.0}  # Micromoles per liter!
# Chlorophyll = {'min': -0.1, 'max': 80.0 } #Using Fluorescence method CPHL
global_range_temperature_ferrybox = {'min': -2.5, 'max': 100.0}

# Thresholds for Local Range Test: 
''' from Source 1 '''
all_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
local_range_chla_fluorescence = [
    {'min': -0.1, 'max': 2.0, 'area': Arctic, 'months': [1, 2, 10, 11, 12]},
    {'min': -0.1, 'max': 12.0, 'area': Arctic, 'months': [3, 4]},
    {'min': -0.1, 'max': 6.0, 'area': Arctic, 'months': [5, 6, 7, 8, 9]},

    {'min': -0.1, 'max': 14.0, 'area': NorthSea, 'months': [1, 2, 3, 4, 5, 6]},
    {'min': -0.1, 'max': 8.0, 'area': NorthSea, 'months': [7, 8]},
    {'min': -0.1, 'max': 12.0, 'area': NorthSea, 'months': [9, 10, 11, 12]},
    # The definition of the baltic region does not match source 1 and invalidates good values in skattegate
    # TODO: fix the baltic region and split it up into it's document sub regions as described in source 1
    {'min': -0.1, 'max': 80.0, 'area': Baltic, 'months': all_months},
    # {'min': 0.5, 'max': 25.0, 'area': Baltic, 'months': [1, 2, 10, 11, 12]},
    # {'min': 1.5, 'max': 77.6, 'area': Baltic, 'months': [3, 4, 5]},
    # {'min': 0.5, 'max': 36.8, 'area': Baltic, 'months': [6, 7, 8, 9]},

    {'min': -0.1, 'max': 20.0, 'area': NW_Shelf,
     'months': [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    {'min': -0.1, 'max': 20.0, 'area': NW_Shelf,
     'months': [10, 11, 12]}
]

local_range_oxygen = [
    {'min': 0.0, 'max': 500.0, 'area': Arctic, 'months': all_months},
    {'min': 0.0, 'max': 500.0, 'area': NorthSea, 'months': all_months},
    {'min': 0.0, 'max': 500.0, 'area': Baltic, 'months': all_months},
    {'min': 0.0, 'max': 500.0, 'area': NW_Shelf, 'months': all_months},
]

local_range_temperature = [
    {'min': -2.0, 'max': 24.0, 'area': NW_Shelf, 'months': all_months},
    {'min': -2.0, 'max': 30.0, 'area': SW_Shelf, 'months': all_months},
    {'min': -2.0, 'max': 30.0, 'area': Baltic, 'months': all_months},   
    {'min': -2.0, 'max': 24.0, 'area': Arctic, 'months': all_months},
]

local_range_salinity = [
    {'min': 0.0, 'max': 37.0, 'area': NW_Shelf, 'months': all_months},
    {'min': 0.0, 'max': 35.5, 'area': Baltic, 'months': all_months},   
    {'min': 0.0, 'max': 38.0, 'area': SW_Shelf, 'months': all_months},
    {'min': 2.0, 'max': 40.0, 'area': Arctic, 'months': all_months},
]

spike_thresholds = {'temperature': 6, 'salinity': 0.9, 'oxygen': 50}  # Surface only oxygen in micromol/kg
flatness_max_variance = 0.04
# knots
# min threshold 0.5 covers 0.0001 in lon and lat for 1 min sampling
global_range_velocity_ferrybox = {'min': 0.5, 'max': 25}
velocity_max_variance = 0.5
