from typing import List, Optional
from pydantic import BaseModel


class qcinput(BaseModel):
    values: List
    locations: Optional[List]
