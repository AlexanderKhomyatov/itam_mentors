from persistent.db.base import Base, WithId
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

class Mentor(Base, WithId):
    __tablename__ = "mentors"

    telegram_id = Column(String, nullable=True, unique=True)
    name = Column(String, nullable=True)
    info = Column(Text, nullable=True)

    calls = relationship("Call", back_populates="mentor", cascade="all, delete-orphan")
    requests = relationship("Request", back_populates="mentor", cascade="all, delete-orphan")