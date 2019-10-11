# Changelog

All notable changes to this project will be documented in this file.

Example:

## [major.minor.patch]

### Bug Fixes

- some short description of what's fixed

### Features

- added new_test
  - short description of the test

### Breaking Changes

- removed parameter x from some_test

## [4.0.0]

### Breaking change

Changed the function signature of QC.execute. Split the tests dict into:

- measurement_name: str
- tests: Dict[str, bool]

Before:
 ```
    tests = {"temperature" : {
                "local_range_test": False,
                "global_range_test": False,
                "argo_spike_test": True,
                "frozen_test": True,
            }
    }

    QC.execute(platform=qclib.QC.init(platform_code), qc_input=data, tests=tests)
```

After 
```    
    tests = {
        "local_range_test": False,
        "global_range_test": False,
        "argo_spike_test": True,
        "frozen_test": True,
    }

    # in addition we introduced a new param measurement_name. example:
    QC.execute(platform=qclib.QC.init(platform_code), qc_input=data,
    measurement_name="temperature", tests=tests)
```

## [3.0.0]

- made locations required in velocity_from_location_list function

## [2.4.4]
### Bug Fixes

- fixed pump_history_test so that it allows None values
  - If a timeseries for pump is supplied with None values, the test will replace None -> 0 
  - related issue https://github.com/NIVANorge/nivacloud/issues/463

## [0.0.0] - [2.4.3]

all these versions did not have a changelog. Please refer to git history for the remaining history
