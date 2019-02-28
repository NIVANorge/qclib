from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class Measurement(BaseModel):
    value: float
    datetime: datetime


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



