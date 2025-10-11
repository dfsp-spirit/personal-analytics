from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, date
import json

from .models import HealthEntry, HealthEntryCreate, HealthEntryRead, HealthEntryUpdate

# Simple in-memory storage for now - replace with database later
entries_db: List[HealthEntry] = []

app = FastAPI(title="Personal Analytics API", version="0.1.0")

# CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/entries/", response_model=HealthEntryRead)
async def submit_entry(entry: HealthEntryCreate):
    """Submit a new daily health entry"""

    # Check if entry for today already exists
    today = datetime.now().date().isoformat()
    existing_entry = next((e for e in entries_db if e.date == today), None)

    if existing_entry:
        raise HTTPException(
            status_code=400,
            detail=f"Entry for today ({today}) already exists. Use PUT to update."
        )

    # Create new entry
    new_entry = HealthEntry(**entry.dict())
    entries_db.append(new_entry)

    return new_entry

@app.put("/entries/{entry_id}", response_model=HealthEntryRead)
async def update_entry(entry_id: str, entry_update: HealthEntryUpdate):
    """Update an existing health entry"""

    # Find entry
    entry_index = next((i for i, e in enumerate(entries_db) if e.id == entry_id), None)

    if entry_index is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Update fields
    update_data = entry_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entries_db[entry_index], field, value)

    return entries_db[entry_index]

@app.get("/entries/", response_model=List[HealthEntryRead])
async def read_all_entries(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get all health entries with optional filtering"""

    filtered_entries = entries_db

    # Date filtering
    if start_date:
        filtered_entries = [e for e in filtered_entries if e.date >= start_date]
    if end_date:
        filtered_entries = [e for e in filtered_entries if e.date <= end_date]

    # Sort by date descending (newest first)
    filtered_entries.sort(key=lambda x: x.date, reverse=True)

    return filtered_entries[skip:skip + limit]

@app.get("/entries/today", response_model=Optional[HealthEntryRead])
async def read_today_entry():
    """Get today's entry if it exists"""
    today = datetime.now().date().isoformat()
    return next((e for e in entries_db if e.date == today), None)

@app.get("/entries/{entry_id}", response_model=HealthEntryRead)
async def read_entry(entry_id: str):
    """Get a specific entry by ID"""
    entry = next((e for e in entries_db if e.id == entry_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str):
    """Delete an entry"""
    global entries_db
    initial_length = len(entries_db)
    entries_db = [e for e in entries_db if e.id != entry_id]

    if len(entries_db) == initial_length:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"message": "Entry deleted successfully"}

# Health check
@app.get("/")
async def root():
    return {"message": "Personal Analytics API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "entries_count": len(entries_db)}
