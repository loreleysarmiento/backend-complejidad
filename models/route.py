import enum

class RouteCriteriaEnum(str, enum.Enum):
    DISTANCE = "distance"
    COST = "cost"


from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Numeric,
    Float,
    String,
    func,
)
from sqlalchemy.orm import relationship
from db.base import Base
import enum


class RouteCriteriaEnum(str, enum.Enum):
    DISTANCE = "distance"
    COST = "cost"


class RouteCalculated(Base):
    __tablename__ = "routes_calculated"

    id = Column(Integer, primary_key=True, index=True)  # route_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    origin_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    destiny_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    total_distance = Column(Float, nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False)
    query_date = Column(DateTime(timezone=True), server_default=func.now())
    criteria = Column(String(20), nullable=False)  # 'distance' o 'cost'
    total_stops = Column(Integer, nullable=False, default=0)
    algorithm = Column(String(30), nullable=False, default="dijkstra")

    user = relationship("User", back_populates="routes")
    details = relationship("RouteDetail", back_populates="route", cascade="all, delete-orphan")


class RouteDetail(Base):
    __tablename__ = "route_details"

    id = Column(Integer, primary_key=True, index=True)  # detail_id
    route_id = Column(Integer, ForeignKey("routes_calculated.id"), nullable=False)
    route_order = Column(Integer, nullable=False)  # 0..n
    airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)

    route = relationship("RouteCalculated", back_populates="details")