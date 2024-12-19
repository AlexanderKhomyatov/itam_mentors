from persistent.db.base import Base, WithId
from sqlalchemy import Column, Boolean, Integer, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Call(Base, WithId):
    __tablename__ = "calls"

    day = Column(Integer, nullable=False)
    time = Column(Time, nullable=False)
    is_reserved = Column(Boolean, default=False, nullable=False)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"), nullable=False)

    mentor = relationship("Mentor", back_populates="calls")
    request = relationship("Request", back_populates="call", uselist=False)