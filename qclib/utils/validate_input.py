import logging
import pandas as pd
import datetime
from .qc_input import QCInput_df
from .transform_input import merge_data, merge_data_spike


def validate_additional_data(qcinput: QCInput_df):
    """This function checks validity of additional data
    if additional data have time gaps, they are reset to empty"""

    def validate_data_for_time_gaps(df, fuzzy_seconds: int = 0) -> bool:
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

    is_valid = True
    if qcinput.historical_data is not None and len(qcinput.historical_data) > 1:
        df = merge_data(qcinput.current_data, qcinput.historical_data)
        duplicates = df.duplicated(subset="time").any()
        assert duplicates == False, "duplicated time stamps in historical data"
        assert qcinput.current_data["time"].iloc[0] > qcinput.historical_data["time"].iloc[0], \
            "future data while historical data are expected"
        if not validate_data_for_time_gaps(df):
            is_valid = False
            qcinput.historical_data = pd.DataFrame.from_dict({})
            logging.warning("Removing historical data due to time gaps")

    if qcinput.future_data is not None and len(qcinput.future_data) > 1:
        df = merge_data(qcinput.current_data, qcinput.future_data)
        duplicates = df.duplicated(subset="time").any()
        assert duplicates == False, "duplicated time stamps in future data"
        assert qcinput.current_data["time"].iloc[0] < qcinput.future_data["time"].iloc[0], \
            "historical data while future data are expected"
        if not validate_data_for_time_gaps(df):
            is_valid = False
            qcinput.future_data = pd.DataFrame.from_dict({})
            logging.warning("Removing future data due to time gaps")

    if qcinput.historical_data is not None and qcinput.future_data is not None and \
            len(qcinput.future_data) == 1 and len(qcinput.historical_data) == 1:
        df = merge_data_spike(qcinput.current_data, qcinput.future_data, qcinput.historical_data)
        if not validate_data_for_time_gaps(df):
            is_valid = False
            qcinput.future_data = pd.DataFrame.from_dict({})
            qcinput.historical_data = pd.DataFrame.from_dict({})
            logging.warning("Removing additional data for spike test due to time gaps")

    return is_valid

