from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import numpy as np


class Measurement(BaseModel):
    datetime: datetime
    value: float


class Location(BaseModel):
    datetime: datetime
    lon: float
    lat: float


class QCInput(BaseModel):
    value: float
    timestamp: datetime
    longitude: Optional[float]
    latitude: Optional[float]
    historical_data: List[Measurement]
    future_data: List[Measurement]


class QCInput_df(BaseModel):
    current_data: Any
    longitude: Optional[float]
    latitude: Optional[float]
    historical_data: Any
    future_data: Any


class qcinput(BaseModel):
    values: List
    locations: List
