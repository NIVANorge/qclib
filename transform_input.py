import pandas as pd


def merge_data(df, df_delayed):
    if df_delayed is None:
        return df
    df_delayed = df_delayed.sort_values(by='time', ascending=False)
    col_name = df_delayed.columns.values[0]
    df_delayed.rename(columns={col_name: 'data'}, inplace=True)
    df_delayed["time"] = df_delayed.index.get_values()
    result = pd.concat([df, df_delayed], sort=True)
    return result
