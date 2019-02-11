from typing import Optional
from datetime import datetime


class QCInput:

    value: float
    timestamp: datetime
    longitude: Optional[float]
    latitude: Optional[float]
    historical_data: Optional

    def __init__(self, value, timestamp, longitude=None, latitude=None, historical_data=None):
        self.value = value
        self.timestamp = timestamp
        self.longitude = longitude
        self.latitude = latitude
        self.historical_data = historical_data
