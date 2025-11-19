from sqlalchemy import Column, Integer, ForeignKey, Float, Numeric
from sqlalchemy.orm import relationship
from db.base import Base


class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)  # connection_id
    airport_a_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    airport_b_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    distance_km = Column(Float, nullable=False)
    congestion_factor = Column(Float, nullable=False, default=1.0)
    cost = Column(Numeric(10, 2), nullable=False)

    airport_a = relationship("Airport", foreign_keys=[airport_a_id], back_populates="connections_from")
    airport_b = relationship("Airport", foreign_keys=[airport_b_id], back_populates="connections_to")
