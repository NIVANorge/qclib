from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import pandas as pd

class QCInput(BaseModel):
    value: float
    timestamp: datetime
    longitude: Optional[float]
    latitude: Optional[float]
    historical_data: Optional[pd.DataFrame]
