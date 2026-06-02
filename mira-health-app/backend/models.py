from sqlalchemy import Column, String, Float, Date, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid

class Patient(Base):
    __tablename__ = "patients"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name   = Column(String, nullable=False)
    dob         = Column(Date, nullable=False)
    email       = Column(String, unique=True, nullable=False)
    glucose     = Column(Float, nullable=False)
    haemoglobin = Column(Float, nullable=False)
    cholesterol = Column(Float, nullable=False)
    remarks     = Column(String, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())