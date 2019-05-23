from typing import List, Optional
from pydantic import BaseModel


class QCInput(BaseModel):
    values: List
    locations: Optional[List]
