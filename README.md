# Installing

Install from https://pypi.org/:
```
pip install nivacloud-qclib
```


# Standalone module containing quality tests

Input to the libary is a qcinput stucture which contains two lists:

1. Values: it is a list of lists [[],[],[],...], where inner list is [datetime, value]
2. Locations: is it a list of lists [[],[],[],...], where inner list is [datetime, lon, lat] and it is optional

Data *has to* be sorted ascending in time (first element in the list is the oldest, last element is the newest)

and a dictionary `tests`, where key is the measurement name 
(e.g. temperature, or salinity, or...) and the value is a 
list of tests =["global_range","local_range"]...


# QC.py

A simple interface to facilitate execution of QC tests during ingest phase.
It contains a platform_dict to relate platform_code to the relevant QC class and
the three functions:
1. init(platform_code) instatiates (creates obj of) a relevant platform class. If platform_code is not found in platform_dict a PlatformQC is instatiated.
2. execute(platform, qc_input, measurement_name, tests) calls applyQC function defined in PlatformsQC.
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

    pip install -e . 


# Changelog

Whenever we release a new version, the changes should be listed in [CHANGELOG.md](CHANGELOG.md)
