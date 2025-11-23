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
        # En Pydantic v2 reemplaza a orm_mode = True
        from_attributes = True
