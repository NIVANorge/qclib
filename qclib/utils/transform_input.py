import datetime
import pandas as pd
from .qc_input import QCInput_df, QCInput
from .measurement import measurement_list_to_dataframe


def merge_data(df, df_additional):
    if df_additional is None:
        return df
    if df["time"].iloc[0] > df_additional["time"].iloc[0]:
        result = pd.concat([df_additional, df], ignore_index=True, sort=False)
    else:
        result = pd.concat([df, df_additional], ignore_index=True, sort=False)
    return result


def merge_data_spike(df_hist, df, df_future):
    if df_hist is None and df_future is None:
        return df
    result = pd.concat([df_hist, df, df_future], ignore_index=True, sort=False)
    return result


def transform_input_to_df(qcinput: QCInput) -> QCInput_df:

    historical_values_df = measurement_list_to_dataframe(qcinput.historical_data)
    future_values_df = measurement_list_to_dataframe(qcinput.future_data)
    current_data_df = pd.DataFrame.from_dict({"data": [qcinput.value], "time": [qcinput.timestamp]})
    qcinput_df = QCInput_df(current_data=current_data_df, longitude=qcinput.longitude, latitude=qcinput.latitude,
                            historical_data=historical_values_df, future_data=future_values_df)
    return qcinput_df
