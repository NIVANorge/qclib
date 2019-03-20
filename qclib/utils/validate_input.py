import logging
import pandas as pd
import datetime
from .qc_input import QCInput_df
from .transform_input import merge_data, merge_data_spike


def has_duplicates(df: pd.DataFrame) -> bool:
    duplicates = df.duplicated(subset="time").any()
    return duplicates


def has_time_reversed(current_data_df: pd.DataFrame, additional_data_df: pd.DataFrame, mode: int) -> bool:
    if mode == 1:
        reversed = current_data_df["time"].iloc[0] < additional_data_df["time"].iloc[0]
    else:
        reversed = current_data_df["time"].iloc[0] > additional_data_df["time"].iloc[0]

    return reversed


def validate_data_for_time_gaps(df: pd.DataFrame, fuzzy_seconds: int = 0) -> bool:
    """
    Validates that the given dataframe has no time gaps between signals.

    if fuzzy_seconds is specified, time gaps lower than fuzzy_seconds will
    be considered not a time gap

    Assumes a dataframe with a time column and is sorted on time (ascending or decending does not matter)
    """

    def has_timegaps(dt, first_dt):
        return abs(dt - first_dt) <= datetime.timedelta(seconds=fuzzy_seconds)

    dt_list = df['time'].diff().dropna()
    first_dt = dt_list.iloc[0]
    no_time_gaps = all(has_timegaps(dt, first_dt) for dt in dt_list)
    return no_time_gaps


def validate_data(current_data_df: pd.DataFrame, additional_data_df: pd.DataFrame, mode: int) -> bool:
    is_valid = True
    if additional_data_df is not None and len(additional_data_df) > 1:
        df = merge_data(current_data_df, additional_data_df)
        assert has_duplicates(df) == False, "duplicated time stamps in historical data"
        assert has_time_reversed(current_data_df, additional_data_df, mode) == False, \
            "historical data are future in time or future data are historical"
        is_valid = validate_data_for_time_gaps(df, fuzzy_seconds=1)
    return is_valid


def validate_data_for_spike(current_data_df: pd.DataFrame, additional_data_df: pd.DataFrame,
                            additional_data_df2: pd.DataFrame) -> bool:
    is_valid = True
    if additional_data_df is not None and additional_data_df2 is not None and \
            len(additional_data_df) == 1 and len(additional_data_df2) == 1:
        df = merge_data_spike(current_data_df, additional_data_df, additional_data_df2)
        assert has_duplicates(df) == False, "duplicated time stamps in historical data"
        is_valid = validate_data_for_time_gaps(df, fuzzy_seconds=1)
    return is_valid


def validate_additional_data(qcinput: QCInput_df):
    """This function checks validity of additional data
    if additional data have time gaps, they are reset to empty"""

    is_valid = True
    if not validate_data(qcinput.current_data, qcinput.historical_data, 1):
        is_valid = False
        qcinput.historical_data = pd.DataFrame.from_dict({})
        logging.warning("Removing historical data due to time gaps")

    if not validate_data(qcinput.current_data, qcinput.future_data, 2):
        is_valid = False
        qcinput.future_data = pd.DataFrame.from_dict({})
        logging.warning("Removing future data due to time gaps")

    if not validate_data_for_spike(qcinput.current_data, qcinput.historical_data, qcinput.future_data):
        qcinput.future_data = pd.DataFrame.from_dict({})
        qcinput.historical_data = pd.DataFrame.from_dict({})
        logging.warning("Removing additional data due to time gaps")

    return is_valid
