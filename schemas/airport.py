from pydantic import BaseModel
from typing import Optional 

class AirportRead(BaseModel):
    id: int
    name: str        
    city: Optional[str] = None
    country: str
    lat: float
    lon: float

    class Config:
        from_attributes = True
