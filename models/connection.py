from sqlalchemy import Column, Integer, ForeignKey, Float, Numeric
from sqlalchemy.orm import relationship
from db.base import Base


class Connection(Base):
    __tablename__ = "Conexiones"

    id = Column("conection_id", Integer, primary_key=True, index=True)

    airport_a_id = Column(
        "airport_a",
        Integer,
        ForeignKey("Aeropuertos.id"),
        nullable=False,
    )
    airport_b_id = Column(
        "airport_b",
        Integer,
        ForeignKey("Aeropuertos.id"),
        nullable=False,
    )

    distance_km = Column("distance", Float, nullable=False)
    #congestion_factor = Column(Float, nullable=False, default=1.0)  # si no existe, quítala
    cost = Column(Numeric(10, 2), nullable=False)

    airport_a = relationship("Airport", foreign_keys=[airport_a_id], back_populates="connections_from")
    airport_b = relationship("Airport", foreign_keys=[airport_b_id], back_populates="connections_to")
