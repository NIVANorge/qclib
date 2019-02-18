from typing import Optional, List, Any
from datetime import datetime

from pandas import DataFrame
from pydantic import BaseModel


class QCInput(BaseModel):
    value: float
    timestamp: datetime
    longitude: Optional[float]
    latitude: Optional[float]
    historical_data: Any
    future_data: Any

