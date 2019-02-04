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

# QC.py

A simple interface to facilitate execution of QC tests during ingest phase.
It contains a platform_dict to relate platform_code to the relevant QC class and
the three functions:
1. init(platform_code) instatiates (creates obj of) a relevant platform class. If platform_code is not found in platform_dict a PlatformQC is instatiated.
2. execute(obj, df, tests) calls applyQC function defined in PlatformsQC.
3. finalize() prints success. 


# PlatformQC.py

Contains a global common_tests dictionary and definition of PlatformQC class.
PlatformQC has a constructor which initiated qc_tests to be the same as common_tests.
applyQC method of this class executes the QC functions for each test in qc_tests and stores relevant QC flags.
It also contains methods to format flags.


# Platforms.py
Contains definitions of subclasses for each platform: FerryboxQC, SeaGliderQC, WaveGliderQC, SailbuoyQC.
They all inherit from PlatformQC defined in PlatformQC.py
Constructor in derived class may modify threshold and qc_tests dictionary.
In addition platform specific information such as calibration may be added here.


# QCTests.py 
Contains definition of QCTests class which has a list 
of (static) function definitions for each QC test and a decorator checking number of sample requirements for each test.
This class is a base for PlatformQC.

# Thresholds.py 
Defines threshold values for range tests.


# Version update

In order to update qclib version, update __version__ attribute in qclib/__init__.py


