from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from db.base import Base


class Airport(Base):
    __tablename__ = "airports"

    id = Column(Integer, primary_key=True, index=True)  # airport_id
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    concurrency_level = Column(Integer, nullable=False, default=3)  # 1..5

    # conexiones desde este aeropuerto
    connections_from = relationship(
        "Connection",
        foreign_keys="Connection.airport_a_id",
        back_populates="airport_a",
    )
    connections_to = relationship(
        "Connection",
        foreign_keys="Connection.airport_b_id",
        back_populates="airport_b",
    )
