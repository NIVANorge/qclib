import datetime
import pandas as pd


def merge_data(df, df_delayed):
    if df_delayed is None:
        return df
    result = pd.concat([df_delayed, df], ignore_index=True,sort=False)
    sorted = result.sort_values(by="time", ascending=True)
    return sorted

def merge_data_spike(df_hist, df, df_future):
    if df_hist is None and df_future is None:
        return df
    result = pd.concat([df_hist, df, df_future], ignore_index=True,sort=False)
    sorted = result.sort_values(by="time", ascending=True)
    return sorted

