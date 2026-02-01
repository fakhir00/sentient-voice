from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.types import EncryptedString

class Practice(Base):
    __tablename__ = "practices"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    pms_api_key: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    patients: Mapped[List["Patient"]] = relationship(back_populates="practice")

class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    practice_id: Mapped[int] = mapped_column(ForeignKey("practices.id"))
    
    # Encrypted PII
    first_name: Mapped[str] = mapped_column(EncryptedString(255))
    last_name: Mapped[str] = mapped_column(EncryptedString(255))
    phone: Mapped[str] = mapped_column(EncryptedString(50))
    
    # Relationships
    practice: Mapped["Practice"] = relationship(back_populates="patients")
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED") # SCHEDULED, CANCELLED, COMPLETED
    
    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="appointments")

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    recording_url: Mapped[Optional[str]] = mapped_column(String(512))
    transcript_summary: Mapped[Optional[str]] = mapped_column(Text)
    duration: Mapped[Optional[int]] = mapped_column(Integer) # Seconds
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
