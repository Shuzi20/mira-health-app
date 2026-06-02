from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import ai_service
from database import engine, get_db

# Create all tables in the database on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MIRA Health Prediction API")


# ─── CREATE ───────────────────────────────────────────────
@app.post("/patients", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    
    # Check if email already exists
    existing = db.query(models.Patient).filter(models.Patient.email == patient.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Save patient to database first
    db_patient = models.Patient(
        full_name   = patient.full_name,
        dob         = patient.dob,
        email       = patient.email,
        glucose     = patient.glucose,
        haemoglobin = patient.haemoglobin,
        cholesterol = patient.cholesterol,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    # Call AI and save remarks
    try:
        remarks = ai_service.predict_health(
            full_name   = patient.full_name,
            dob         = str(patient.dob),
            glucose     = patient.glucose,
            haemoglobin = patient.haemoglobin,
            cholesterol = patient.cholesterol,
        )
        db_patient.remarks = remarks
        db.commit()
        db.refresh(db_patient)
    except Exception as e:
        db_patient.remarks = f"AI prediction unavailable: {str(e)}"
        db.commit()

    return db_patient


# ─── READ ALL ─────────────────────────────────────────────
@app.get("/patients", response_model=List[schemas.PatientResponse])
def get_all_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()


# ─── READ ONE ─────────────────────────────────────────────
@app.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ─── UPDATE ───────────────────────────────────────────────
@app.put("/patients/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(patient_id: int, updates: schemas.PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Only update fields that were actually sent
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient


# ─── DELETE ───────────────────────────────────────────────
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return {"message": f"Patient {patient_id} deleted successfully"}