import datetime
import pandas as pd


def merge_data(df, df_delayed):
    if df_delayed is None:
        return df
    result = pd.concat([df_delayed, df])
    result.set_index(["time"])
    sorted = result.sort_values(by="time", ascending=True)
    return sorted


def validate_data_for_time_gaps(df, fuzzy_seconds: int = 0) -> bool:
    """
    Validates that the given dataframe has no time gaps between signals.

    if fuzzy_seconds is specified, time gaps lower than fuzzy_seconds will
    be considered not a time gap

    Assumes a dataframe with a time column and is sorted on time (ascending or decending does not matter)
    """

    def has_timegaps(dt, first_dt):
        return abs(dt - first_dt) <= datetime.timedelta(seconds=fuzzy_seconds)

    dt_list = df["time"].diff().dropna()
    # first row will be dropped as it does not have a delta to itself
    first_dt = dt_list[2]
    no_time_gaps = all(has_timegaps(dt, first_dt) for dt in dt_list)
    return no_time_gaps
