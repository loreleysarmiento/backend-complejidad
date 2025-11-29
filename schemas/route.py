
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class Criteria(str, Enum):
    distance = "distance"
    cost = "cost"

class RouteCalculateRequest(BaseModel):
    origin_id: int
    destiny_id: int
    criteria: Criteria

class RouteHistoryItem(BaseModel):
    id: int
    origin_id: int
    destiny_id: int
    total_distance: float
    total_cost: float
    criteria: str
    total_stops: int
    algorithm: str
    query_date: datetime
    max_stops: int | None = None
    avg_concurrency: float | None = None

    class Config:
        from_attributes = True
