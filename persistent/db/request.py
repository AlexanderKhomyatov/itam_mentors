from persistent.db.base import Base, WithId
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Text, Boolean, DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
import enum

class RequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Request(Base, WithId):
    __tablename__ = "requests"

    call_type = Column(Boolean, nullable=False) # True = call, False = question
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"), nullable=False)
    guest_tg_id = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending, nullable=False)

    mentor = relationship("Mentor", back_populates="requests")
    call = relationship("Call", back_populates="request")