from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from .models import HealthEntry, HealthEntryCreate, HealthEntryRead, HealthEntryUpdate
from .database import get_session, create_db_and_tables

app = FastAPI(title="Personal Analytics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/entries/", response_model=HealthEntryRead)
def submit_entry(entry: HealthEntryCreate, session: Session = Depends(get_session)):
    """Submit a new daily health entry"""

    # Check if entry for today already exists
    today = datetime.now().date().isoformat()
    existing_entry = session.exec(
        select(HealthEntry).where(HealthEntry.date == today)
    ).first()

    if existing_entry:
        raise HTTPException(
            status_code=400,
            detail=f"Entry for today ({today}) already exists. Use PUT to update."
        )

    # Create new entry
    db_entry = HealthEntry.from_orm(entry)
    session.add(db_entry)
    session.commit()
    session.refresh(db_entry)

    return db_entry

@app.put("/entries/{entry_id}", response_model=HealthEntryRead)
def update_entry(entry_id: str, entry_update: HealthEntryUpdate, session: Session = Depends(get_session)):
    """Update an existing health entry"""

    db_entry = session.get(HealthEntry, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Update fields
    update_data = entry_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entry, field, value)

    session.add(db_entry)
    session.commit()
    session.refresh(db_entry)

    return db_entry

@app.get("/entries/", response_model=List[HealthEntryRead])
def read_all_entries(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get all health entries with optional filtering"""

    query = select(HealthEntry)

    if start_date:
        query = query.where(HealthEntry.date >= start_date)
    if end_date:
        query = query.where(HealthEntry.date <= end_date)

    query = query.order_by(HealthEntry.date.desc()).offset(skip).limit(limit)

    entries = session.exec(query).all()
    return entries

@app.get("/entries/today", response_model=Optional[HealthEntryRead])
def read_today_entry(session: Session = Depends(get_session)):
    """Get today's entry if it exists"""
    today = datetime.now().date().isoformat()
    entry = session.exec(
        select(HealthEntry).where(HealthEntry.date == today)
    ).first()
    return entry

@app.get("/entries/{entry_id}", response_model=HealthEntryRead)
def read_entry(entry_id: str, session: Session = Depends(get_session)):
    """Get a specific entry by ID"""
    entry = session.get(HealthEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: str, session: Session = Depends(get_session)):
    """Delete an entry"""
    entry = session.get(HealthEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    session.delete(entry)
    session.commit()

    return {"message": "Entry deleted successfully"}

@app.get("/")
def root():
    return {"message": "Personal Analytics API is running"}

@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    count = session.exec(select(HealthEntry)).all()
    return {"status": "healthy", "entries_count": len(count)}