from typing import Dict, List
from qclib.utils.qc_input import QCInput


def remove_nans(data: QCInput) -> QCInput:
    new_values = []
    new_locations = []
    if data.locations is None:
        new_locations = None

    for i, val in enumerate(data.values):
        if None not in val:
            new_values.append(val)
            if data.locations is not None and len(data.locations) > 0:
                new_locations.append(data.locations[i])
    return QCInput(values=new_values, locations=new_locations)


def flags_resized_to_include_values_for_nan(flags: Dict[str, List[int]], data: QCInput) ->Dict[str, List[int]]:

    size = len(data.values)
    new_flags = {key: [None]*size for key in flags.keys()}
    for key, values in new_flags.items():
        old_flag_index = 0
        for index, new_flag in enumerate(values):
            if None not in data.values[index]:
                new_flags[key][index] = flags[key][old_flag_index]
                old_flag_index = old_flag_index + 1

    return new_flags
