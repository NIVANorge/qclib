import pandas as pd


def merge_data(df, df_delayed):
    if df_delayed is None:
        return df
    df_delayed = df_delayed.sort_values(by='time', ascending=True)
    col_name = df_delayed.columns.values[0]
    df_delayed.rename(columns={col_name: 'data'}, inplace=True)
    df = df.set_index(["time"])
    result = pd.concat([df_delayed, df], sort=True)
    result["time"] = result.index.get_values()
    return result


def validate_data_for_time_gaps(df):
    dt = df["time"].diff().dropna()
    no_time_gaps = all(dt == dt[1])
    assert no_time_gaps == True, "Time gaps in data"
