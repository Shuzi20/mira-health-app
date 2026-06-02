from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
from typing import Optional

class PatientCreate(BaseModel):
    full_name   : str
    dob         : date
    email       : EmailStr
    glucose     : float
    haemoglobin : float
    cholesterol : float

    @field_validator("dob")
    def dob_must_be_past(cls, value):
        if value >= date.today():
            raise ValueError("Date of birth must be in the past")
        return value

    @field_validator("glucose", "haemoglobin", "cholesterol")
    def values_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Blood test values must be positive numbers")
        return value

class PatientUpdate(BaseModel):
    full_name   : Optional[str]   = None
    dob         : Optional[date]  = None
    email       : Optional[str]   = None
    glucose     : Optional[float] = None
    haemoglobin : Optional[float] = None
    cholesterol : Optional[float] = None

class PatientResponse(BaseModel):
    id          : str        # UUID string
    full_name   : str
    dob         : date
    email       : str
    glucose     : float
    haemoglobin : float
    cholesterol : float
    remarks     : Optional[str] = None

    class Config:
        from_attributes = True