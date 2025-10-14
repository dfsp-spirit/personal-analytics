from fastapi import FastAPI, HTTPException, Request, status, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
import logging
import uuid
from typing import List, Optional
from datetime import datetime, timedelta


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
    expose_headers=["X-Operation"]
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add this exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    error_id = str(uuid.uuid4())

    # Log detailed error information server-side
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.error(
        f"Request Validation error ID {error_id}: "
        f"Path: {request.url.path}, "
        f"Errors: {error_details}, "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    # Send generic error to client
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request data",
            "error_id": error_id,
            "message": "Please check your request data format and values"
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # Generate a unique error ID for tracking
    error_id = str(uuid.uuid4())

    # Log detailed error information server-side
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.error(
        f"Validation error ID {error_id}: "
        f"Path: {request.url.path}, "
        f"Errors: {error_details}, "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    # Send generic error to client
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request data",
            "error_id": error_id,  # Client can reference this if needed
            "message": "Please check your request data format and values"
        }
    )


@app.post("/entries/", response_model=HealthEntryRead)
def submit_entry(entry: HealthEntryCreate, session: Session = Depends(get_session)):
    # Use the date from the submitted entry, not today!
    target_date = entry.date

    # Calculate day_of_week from the date (Monday=0, Sunday=6)
    date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    entry.day_of_week = date_obj.weekday()  # Auto-populate the day_of_week field

    existing_entry = session.exec(
        select(HealthEntry).where(HealthEntry.date == target_date)  # ← Changed from today to target_date
    ).first()

    if existing_entry:
        # Update existing entry - EXCLUDE DATE from updates
        update_data = entry.dict(exclude_unset=True, exclude={'date'})  # Critical: exclude date
        for field, value in update_data.items():
            setattr(existing_entry, field, value)

        session.add(existing_entry)
        session.commit()
        session.refresh(existing_entry)

        return Response(
             content=existing_entry.json(),
             status_code=200,
             headers={"X-Operation": "updated"}
        )
    else:
        # Create new entry
        db_entry = HealthEntry.from_orm(entry)
        session.add(db_entry)
        session.commit()
        session.refresh(db_entry)

        return Response(
             content=db_entry.json(),
             status_code=201,
             headers={"X-Operation": "created"}
        )


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


@app.get("/stats/metrics-over-time")
def get_metrics_over_time(
    days: int = 30,  # Default to last 30 days
    metrics: List[str] = None,  # Optional: specific metrics to return
    session: Session = Depends(get_session)
):
    """Get metrics data for visualization over time"""

    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Query entries in date range
    query = select(HealthEntry).where(
        HealthEntry.date >= start_date.isoformat(),
        HealthEntry.date <= end_date.isoformat()
    ).order_by(HealthEntry.date)

    entries = session.exec(query).all()

    # Default metrics if none specified
    if metrics is None:
        metrics = ["mood", "pain", "anxiety", "energy", "sleep_quality"]

    # Structure data for frontend
    result = {
        "dates": [],
        "metrics": {metric: [] for metric in metrics}
    }

    for entry in entries:
        result["dates"].append(entry.date)
        for metric in metrics:
            value = getattr(entry, metric, None)
            result["metrics"][metric].append(value)

    return result