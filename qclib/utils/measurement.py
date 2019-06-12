from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union


Value = Union[float, None]
Measurement = Tuple[datetime, Value]
Location = Tuple[datetime, Value, Value]
