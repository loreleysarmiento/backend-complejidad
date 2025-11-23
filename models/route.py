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
    __tablename__ = "RutasCalculadas"

    id = Column("route_id", Integer, primary_key=True, index=True)

    user_id = Column("user_id", Integer, ForeignKey("Usuarios.user_id"), nullable=False)
    origin_id = Column("origin_id", Integer, ForeignKey("Aeropuertos.airport_id"), nullable=False)
    destiny_id = Column("destiny_id", Integer, ForeignKey("Aeropuertos.airport_id"), nullable=False)

    total_distance = Column(Float, nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False)
    query_date = Column(DateTime(timezone=True), server_default=func.now())
    criteria = Column(String(20), nullable=False)
    total_stops = Column(Integer, nullable=False, default=0)
    algorithm = Column(String(30), nullable=False, default="dijkstra")

    user = relationship("User", back_populates="routes")
    details = relationship("RouteDetail", back_populates="route", cascade="all, delete-orphan")


class RouteDetail(Base):
    __tablename__ = "DetalleRuta"

    id = Column("detail_id", Integer, primary_key=True, index=True)

    route_id = Column(
        "route_id",
        Integer,
        ForeignKey("RutasCalculadas.route_id"),
        nullable=False,
    )

    route_order = Column(Integer, nullable=False)
    airport_id = Column(
        "airport_id",
        Integer,
        ForeignKey("Aeropuertos.airport_id"),
        nullable=False,
    )

    route = relationship("RouteCalculated", back_populates="details")
