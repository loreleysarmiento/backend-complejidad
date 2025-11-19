from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from db.base import Base


class User(Base):
    __tablename__ = "Usuarios"

    id = Column("user_id", Integer, primary_key=True, index=True)
    username = Column("username",String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    routes = relationship("RouteCalculated", back_populates="user")
