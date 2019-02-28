from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional

import pandas as pd
from pydantic import BaseModel


class Measurement(BaseModel):
    value: float
    datetime: datetime


class GpsTrack(BaseModel):
    latitude: float
    longitude: float
    datetime: datetime


def measurement_list_to_dataframe(measurements: List[Measurement]):
    values = [m.value for m in measurements]
    dates = [m.datetime for m in measurements]
    df = pd.DataFrame({"data": values, "time": dates})
    return df
