import pandas as pd
import datetime
import time
from .qc_input import QCInput_df
from .transform_input import merge_data
import numpy as np

def has_duplicates(df: pd.DataFrame) -> bool:
    duplicates = df.duplicated(subset="time").any()
    return duplicates


def has_time_reversed(current_data_df: pd.DataFrame, additional_data_df: pd.DataFrame, mode: int) -> datetime:
    if mode == 1:
        are_data_wrong_time = current_data_df["time"].iloc[0] < additional_data_df["time"].iloc[0]
    else:
        are_data_wrong_time = current_data_df["time"].iloc[0] > additional_data_df["time"].iloc[0]

    return are_data_wrong_time


def check_sort_asc(df: pd.DataFrame):
    return df["time"].iloc[0] <= df["time"].iloc[-1]


def remove_data_after_time_gap(df: pd.DataFrame, time_error: int = 0, mode: int = 1) -> int:
    def _has_timegaps(dt, first_dt):
        return abs(dt - first_dt) <= time_error

    sampling_interval_list = df['time'].diff().dropna()
    sampling_interval_list_sec = [d.total_seconds() for d in sampling_interval_list]
    sampling_interval = np.median(sampling_interval_list_sec)
    no_time_gaps = [_has_timegaps(dt, sampling_interval) for dt in sampling_interval_list_sec]
    if not all(no_time_gaps):
        first_gap_index = next(i for i, v in enumerate(no_time_gaps) if v==False)
        if mode == 1:
            df.drop(df.index[0:first_gap_index + 1], inplace=True)
        else:
            df.drop(df.index[first_gap_index+1:], inplace=True)

    return sampling_interval


def validate_additional_data(qcplatform, qcinput: QCInput_df):
    # Validate historical data
    if qcinput.historical_data is not None and len(qcinput.historical_data) > 0:
        assert check_sort_asc(qcinput.historical_data) == True, "desc sort in time of historical data"
        df = merge_data(qcinput.current_data, qcinput.historical_data)
        assert has_duplicates(df) == False, "duplicated time stamps in historical data"
        assert has_time_reversed(qcinput.current_data, qcinput.historical_data, 1) == False, \
            "historical data are future in time"
        sampling_int_hist = remove_data_after_time_gap(df, time_error=qcplatform.accept_time_difference, mode=1)
        df.drop(df.index[[-1]], inplace=True)
        qcinput.historical_data = df
    # Validate future data
    if qcinput.future_data is not None and len(qcinput.future_data) > 0:
        assert check_sort_asc(qcinput.future_data) == True, "desc sort in time of future data"
        df = merge_data(qcinput.current_data, qcinput.future_data)
        assert has_duplicates(df) == False, "duplicated time stamps in future data"
        assert has_time_reversed(qcinput.current_data, qcinput.future_data, 2) == False, \
            "future data are historical in time"
        sampling_int_future = remove_data_after_time_gap(df, time_error=qcplatform.accept_time_difference, mode=2)
        df.drop(df.index[[0]], inplace=True)
        qcinput.future_data = df
    # Special case: we have just 1 historical and 1 future samples, we need to check weather
    # data are valid for spike test
    if qcinput.future_data is not None and len(qcinput.future_data) > 0 and \
            qcinput.historical_data is not None and len(qcinput.historical_data) > 0:
        if len(qcinput.future_data) == 1 or len(qcinput.historical_data) == 1:
            if abs(sampling_int_hist - sampling_int_future) > qcplatform.accept_time_difference:
                qcinput.future_data = pd.DataFrame.from_dict({})
                qcinput.historical_data = pd.DataFrame.from_dict({})
