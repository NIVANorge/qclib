from typing import List
from .qc_input import QCInput
import numpy as np


def validate_data_for_argo_spike_test(data: QCInput) -> List[bool]:

    def is_valid(val, index):
        if index == 0 or index == len(data.values) - 1:
            return False
        else:
            return max(val[index] - val[index - 1], val[index + 1] - val[index]) < \
                    2 * min(val[index] - val[index - 1], val[index + 1] - val[index])

    values = np.array(data.values)[:, 0]
    return [is_valid(values, i) for i in range(0, len(data.values))]


def initial_flags_for_historical_test(qc_input: QCInput, historical_size: int,
                                      allowed_frequency_difference: float = 2.1) -> np.ndarray:
    """When a test requires a number of historical points these should be reasonable close in time, also the points that
    don't have enough historical points should be marked as cannot run (qc=0)"""

    time_stamps = np.array(qc_input.values)[:, 0]
    flags = np.zeros(len(time_stamps), dtype=int)

    # Instantiate the flags as (qc=1) if it is possible to run the test, otherwise leave as (qc=0)
    time_diff_arrays = [np.diff(np.array(time_stamps[i - historical_size: i + 1]))
                        for i in range(historical_size, len(time_stamps))]
    timestamps_are_consecutive = [all(time_diffs < allowed_frequency_difference * np.median(time_diffs))
                                  for time_diffs in time_diff_arrays]
    flags[[False] * historical_size + timestamps_are_consecutive] = 1

    return flags


def assert_is_sorted(data: QCInput):
    assert data.values[0][0] <= data.values[-1][0], f"Input data has to be sorted ascending: {data.values}"
    if data.locations is not None and len(data.locations) > 1:
        assert data.locations[0][0] <= data.locations[-1][0], f"Input data has to be sorted ascending: {data.locations}"
