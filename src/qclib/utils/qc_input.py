from typing import List, Optional

from pydantic import BaseModel

from qclib.utils.measurement import Measurement, Location


class QCInput(BaseModel):
    values: List[Measurement]
    locations: Optional[List[Location]]
