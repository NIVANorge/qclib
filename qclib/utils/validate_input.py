import pandas as pd
import datetime
from .qc_input import QCInput_df
from .transform_input import merge_data


def has_duplicates(df: pd.DataFrame) -> bool:
    duplicates = df.duplicated(subset="time").any()
    return duplicates


def has_time_reversed(current_data_df: pd.DataFrame, additional_data_df: pd.DataFrame, mode: int) -> datetime:
    if mode == 1:
        reversed = current_data_df["time"].iloc[0] < additional_data_df["time"].iloc[0]
    else:
        reversed = current_data_df["time"].iloc[0] > additional_data_df["time"].iloc[0]

    return reversed


def remove_data_after_time_gap(df: pd.DataFrame, time_error: int = 0) -> int:
    def _has_timegaps(dt, first_dt):
        return abs(dt - first_dt) <= datetime.timedelta(seconds=time_error)

    dt_list = df['time'].diff().dropna()
    first_dt = dt_list.iloc[0]
    no_time_gaps = [_has_timegaps(dt, first_dt) for dt in dt_list]
    if not all(no_time_gaps):
        gen = (i for i, v in enumerate(no_time_gaps) if v is False)
        first_gap_index = next(gen)
        df.drop(df.index[first_gap_index + 1:], inplace=True)
    return first_dt


def validate_additional_data(qcplatform, qcinput: QCInput_df):
    # Validate historical data
    if qcinput.historical_data is not None:
        df = merge_data(qcinput.current_data, qcinput.historical_data)
        assert has_duplicates(df) == False, "duplicated time stamps in historical data"
        assert has_time_reversed(qcinput.current_data, qcinput.historical_data, 1) == False, \
            "historical data are future in time"
        sampling_int_hist = remove_data_after_time_gap(df, time_error=qcplatform.accept_time_difference)
        df.drop(df.index[[-1]], inplace=True)
        qcinput.historical_data = df
    # Validate future data
    if qcinput.future_data is not None:
        df = merge_data(qcinput.current_data, qcinput.future_data)
        assert has_duplicates(df) == False, "duplicated time stamps in historical data"
        assert has_time_reversed(qcinput.current_data, qcinput.future_data, 2) == False, \
            "future data are historical in time"
        sampling_int_future = remove_data_after_time_gap(df, time_error=qcplatform.accept_time_difference)
        df.drop(df.index[[0]], inplace=True)
        qcinput.future_data = df
    # Special case: we have just 1 historical and 1 future samples, we need to check weather
    # data are valid for spike test
    if qcinput.future_data is not None and len(qcinput.future_data) == 1 and \
            qcinput.historical_data is not None and len(qcinput.historical_data) == 1:
        if abs(sampling_int_hist - sampling_int_future) \
                > datetime.timedelta(seconds=qcplatform.accept_time_difference):
            qcinput.future_data = pd.DataFrame.from_dict({})
            qcinput.historical_data = pd.DataFrame.from_dict({})
