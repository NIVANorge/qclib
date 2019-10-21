from datetime import datetime
from typing import Tuple, Union


Value = Union[float, None]
Measurement = Tuple[datetime, Value]
Location = Tuple[datetime, Value, Value]
