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


def validate_data_for_frozen_test(data: QCInput, size) -> List[bool]:

    def is_valid(val, index):
        if index < size:
            return False
        else:
            val_diff = np.diff(np.array(val[-size + index: index+1])[:, 0])
            return all(val_diff < 2.1 * np.median(val_diff))

    return [is_valid(data.values, i) for i in range(0, len(data.values))]


def assert_is_sorted(data: QCInput):
    assert data.values[0][0] <= data.values[-1][0], f"Input data has to be sorted ascending: {data.values}"
    if data.locations is not None and len(data.locations) > 1:
        assert data.locations[0][0] <= data.locations[-1][0], f"Input data has to be sorted ascending: {data.locations}"
