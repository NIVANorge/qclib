# Standalone module containing quality tests

Input to the libary is a `dataframe` with the following column names:
1. name (platform code)
2. longitude
3. latitude
4. data, where data is one measurement e.g. salinity or temperature, or fdom, etc.,..

and a dictionary `tests`, where key is the measurement name 
(e.g. temperature, or salinity, or...) and the value is a 
list of tests =["global_range","local_range"]...

The `dataframe` is indexed with timestamps. 
QC should be performed for the latest timestamp (the first in the `dataframe`),
the remaining data points are provided if they are required by any of the tests.
Number of extra data points is as an argument to a decorator for each test in QCTests.

# PlatformQC.py

Contains definition of PlatformQC class.
applyQC method of this class executes the QC functions for each test and stores relevant QC flags.
Apart from applyQC methods, there are several more functions which seem unused(?)


# Platforms.py
Contains definitions of subclasses for each platform: FerryboxQC, SeaGliderQC, WaveGliderQC, SailbuoyQC 
which hold platform specific information.
They all inherit from common base, which is PlatformQC defined in PlatformQC.py
For now sampling frequency (important for fetching additional data during ingestion) is specified for ferryboxQC class.
In the future these subclasses can hold information about additional tests or calibration constants, etc.


# QCTests.py 
Contains definition of QCTests class which has a list 
of (static) function definitions for each QC test and a decorator checking number of sample requirements for each test.
A global array common_test specifies tests which are common for all platforms.

# Thresholds.py 
Defines threshold values for range tests.


# (Missing) features

1. Only range_test and missing_value has been adjusted to the new interface ( new input )
2. Only range_test and missing_value tests have information on required number of datapoints.
3. Lack of timestamp info for the flags. It is assumed that flags correspond to the latest 
   timestamp. This is not true for spike test.   
4. Lack of logic testing

Note that geographical information (latitude and longitude) is only provided for the latest
timestamp.