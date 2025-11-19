from pydantic import BaseModel

class AirportRead(BaseModel):
    id: int
    name: str        
    city: str
    country: str
    lat: float
    lon: float

    class Config:
        # En Pydantic v2 reemplaza a orm_mode = True
        from_attributes = True
