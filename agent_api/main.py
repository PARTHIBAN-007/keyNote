from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import extract, desc
from datetime import datetime
from typing import List

from src import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/events/", response_model=schemas.EventRead)
def create_event(event: schemas.EventCreate, db: Session = Depends(database.get_db)):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=List[schemas.EventRead])
def get_events(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=1900, le=2100),
    db: Session = Depends(database.get_db)
):
    events = db.query(models.Event).filter(
        extract('month', models.Event.start_time) == month,
        extract('year', models.Event.start_time) == year
    ).all()
    return events

@app.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(database.get_db)):
    now = datetime.now()
    
    upcoming = db.query(models.Event).filter(
        models.Event.start_time >= now
    ).order_by(models.Event.start_time.asc()).limit(5).all()
    
    recent = db.query(models.Event).filter(
        models.Event.end_time < now
    ).order_by(models.Event.end_time.desc()).limit(5).all()
    
    return {"upcoming": upcoming, "recent": recent}

@app.get("/")
def read_root():
    return {"message": "Welcome to KeyNote AI Event Manager"}

