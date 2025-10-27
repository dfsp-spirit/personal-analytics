from fastapi import FastAPI, HTTPException, Request, status, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
import logging
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import json
import io
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from urllib.parse import urlparse

from .logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

from . settings import settings
from .models import HealthEntry, HealthEntryCreate, HealthEntryRead, HealthEntryUpdate
from .database import get_session, create_db_and_tables



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Backend starting with allowed origins: {settings.allowed_origins}")
    if settings.debug:
        print(f"Debug mode enabled.")

    logger.info("Running on_startup tasks...")
    create_db_and_tables()

    yield
    # Shutdown
    logger.info("Backend shutting down")


app = FastAPI(title="Personal Analytics API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Operation"] # custom header to tell frontend on submit if the entry was created or updated.
)



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that ensures CORS headers are always set,
    even in case of exceptions.
    Otherwise, an internal server error may appear as a CORS error in the
    browser, which is misleading during development.
    This also creates a unique error ID for tracking and systematic logging.
    """
    error_id = str(uuid.uuid4())

    # Log the actual error
    logger.error(f"Unhandled exception ID {error_id}: {str(exc)}", exc_info=True)

    # Determine status code based on exception type
    status_code = 500
    if isinstance(exc, HTTPException):
        status_code = exc.status_code

    # Create response with CORS headers
    response = JSONResponse(
        status_code=status_code,
        content={
            "detail": "Internal server error",
            "error_id": error_id,
            "message": "Something went wrong on our end"
        }
    )

    # Get the origin from the request
    origin = request.headers.get("origin")

    def is_localhost(origin: str) -> bool:
        """Check if the origin corresponds to localhost."""
        if not origin:
            return False
        try:
            parsed = urlparse(origin)
            return parsed.hostname in ["localhost", "127.0.0.1", "::1"]
        except:
            return False

    # Check if the origin is in our configured allowed origins
    if origin in settings.allowed_origins or is_localhost(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "X-Operation"

    return response


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
    computed_day_of_week = date_obj.weekday()  # Store in variable
    entry.day_of_week = computed_day_of_week

    existing_entry = session.exec(
        select(HealthEntry).where(HealthEntry.date == target_date)  # ← Changed from today to target_date
    ).first()

    if existing_entry:
        # Update existing entry - EXCLUDE DATE from updates
        update_data = entry.dict(exclude_unset=True, exclude={'date'})  # Critical: exclude date
        for field, value in update_data.items():
            setattr(existing_entry, field, value)

        existing_entry.day_of_week = computed_day_of_week

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
        metrics = ["mood", "pain", "energy", "sleep_quality", "sexual_wellbeing"]

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

from sqlalchemy import func, text
from typing import List, Dict, Any
import statistics

@app.get("/stats/weekday-averages")
def get_weekday_averages(session: Session = Depends(get_session)):
    """Get average metrics per weekday"""
    result = session.exec(
        select(
            HealthEntry.day_of_week,
            func.avg(HealthEntry.mood).label('avg_mood'),
            func.avg(HealthEntry.pain).label('avg_pain'),
            func.avg(HealthEntry.energy).label('avg_energy'),
            func.avg(HealthEntry.sleep_quality).label('avg_sleep_quality'),
            func.avg(HealthEntry.sexual_wellbeing).label('avg_sexual_wellbeing'),
            func.count(HealthEntry.id).label('entry_count')
        )
        .group_by(HealthEntry.day_of_week)
        .order_by(HealthEntry.day_of_week)
    ).all()

    # Convert to frontend-friendly format
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    averages = []
    for row in result:
        averages.append({
            'weekday': weekdays[row.day_of_week],
            'day_of_week': row.day_of_week,
            'avg_mood': round(float(row.avg_mood or 0), 2),
            'avg_pain': round(float(row.avg_pain or 0), 2),
            'avg_energy': round(float(row.avg_energy or 0), 2),
            'avg_sleep_quality': round(float(row.avg_sleep_quality or 0), 2),
            'avg_sexual_wellbeing': round(float(row.avg_sexual_wellbeing or 0), 2),
            'entry_count': row.entry_count
        })

    return averages

@app.get("/stats/correlations")
def get_correlations(session: Session = Depends(get_session)):
    """Calculate correlations between different metrics"""
    # Get all entries with the metrics we want to correlate
    entries = session.exec(
        select(
            HealthEntry.mood,
            HealthEntry.pain,
            HealthEntry.energy,
            HealthEntry.sleep_quality,
            HealthEntry.sexual_wellbeing,
            HealthEntry.stress_level_work,
            HealthEntry.stress_level_home
        ).where(
            HealthEntry.mood.isnot(None),
            HealthEntry.pain.isnot(None)
        )
    ).all()

    if not entries:
        return {"error": "Insufficient data for correlation analysis"}

    # Convert to lists for each metric
    metrics_data = {}
    metric_fields = ['mood', 'pain', 'energy', 'sleep_quality', 'sexual_wellbeing', 'stress_level_work', 'stress_level_home']

    for field in metric_fields:
        metrics_data[field] = [getattr(entry, field) for entry in entries if getattr(entry, field) is not None]

    # Calculate correlations
    correlations = []
    for i, metric1 in enumerate(metric_fields):
        for j, metric2 in enumerate(metric_fields):
            if i < j:  # Avoid duplicates and self-correlation
                data1 = metrics_data[metric1]
                data2 = metrics_data[metric2]

                # Ensure we have matching pairs (same length)
                min_len = min(len(data1), len(data2))
                if min_len > 1:
                    corr = statistics.correlation(data1[:min_len], data2[:min_len])
                    correlations.append({
                        'metric1': metric1,
                        'metric2': metric2,
                        'correlation': round(corr, 3),
                        'sample_size': min_len
                    })

    # Sort by absolute correlation strength
    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

    return correlations

@app.get("/stats/lagged-correlations")
def get_lagged_correlations(session: Session = Depends(get_session)):
    """Check if pain today predicts mood tomorrow (and other lagged relationships)"""
    try:
        # Raw SQL for lagged analysis - updated to match your actual model fields
        query = text("""
            WITH daily_entries AS (
                SELECT
                    date,
                    mood,
                    pain,
                    energy,
                    sexual_wellbeing,
                    sleep_quality,
                    stress_level_work,
                    stress_level_home,
                    LAG(mood) OVER (ORDER BY date) as next_day_mood,
                    LAG(pain) OVER (ORDER BY date) as next_day_pain,
                    LAG(energy) OVER (ORDER BY date) as next_day_energy,
                    LAG(sexual_wellbeing) OVER (ORDER BY date) as next_day_sexual_wellbeing,
                    LAG(sleep_quality) OVER (ORDER BY date) as next_day_sleep_quality
                FROM healthentry
                WHERE mood IS NOT NULL AND pain IS NOT NULL
                ORDER BY date
            )
            SELECT
                COUNT(*) as pair_count,
                CORR(pain, next_day_mood) as pain_vs_next_mood,
                CORR(mood, next_day_pain) as mood_vs_next_pain,
                CORR(sexual_wellbeing, next_day_mood) as sexual_wellbeing_vs_next_mood,
                CORR(pain, next_day_energy) as pain_vs_next_energy,
                CORR(sleep_quality, next_day_mood) as sleep_vs_next_mood,
                CORR(stress_level_work, next_day_mood) as work_stress_vs_next_mood,
                CORR(stress_level_home, next_day_mood) as home_stress_vs_next_mood
            FROM daily_entries
            WHERE next_day_mood IS NOT NULL
        """)

        result = session.exec(query).first()

        if not result or result.pair_count < 5:  # Need minimum data points
            return {"error": "Insufficient data for lagged correlation analysis"}

        return {
            'pair_count': result.pair_count,
            'pain_today_vs_mood_tomorrow': round(float(result.pain_vs_next_mood or 0), 3),
            'mood_today_vs_pain_tomorrow': round(float(result.mood_vs_next_pain or 0), 3),
            'sexual_wellbeing_today_vs_mood_tomorrow': round(float(result.sexual_wellbeing_vs_next_mood or 0), 3),
            'pain_today_vs_energy_tomorrow': round(float(result.pain_vs_next_energy or 0), 3),
            'sleep_quality_today_vs_mood_tomorrow': round(float(result.sleep_vs_next_mood or 0), 3),
            'work_stress_today_vs_mood_tomorrow': round(float(result.work_stress_vs_next_mood or 0), 3),
            'home_stress_today_vs_mood_tomorrow': round(float(result.home_stress_vs_next_mood or 0), 3),
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error in lagged-correlations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while calculating correlations"
        )
    except Exception as e:
        logger.error(f"Unexpected error in lagged-correlations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

@app.get("/stats/summary")
def get_summary_stats(session: Session = Depends(get_session)):
    """Get overall summary statistics"""
    result = session.exec(
        select(
            func.count(HealthEntry.id).label('total_entries'),
            func.min(HealthEntry.date).label('first_entry'),
            func.max(HealthEntry.date).label('last_entry'),
            func.avg(HealthEntry.mood).label('avg_mood'),
            func.avg(HealthEntry.pain).label('avg_pain'),
            func.avg(HealthEntry.energy).label('avg_energy'),
            func.avg(HealthEntry.sexual_wellbeing).label('avg_sexual_wellbeing'),
            func.avg(HealthEntry.step_count).label('avg_step_count')
        )
    ).first()

    # Most recent streak of entries
    streak_query = text("""
        WITH dates AS (
            SELECT date::date as entry_date,
                   LAG(date::date) OVER (ORDER BY date) as prev_date
            FROM healthentry
            ORDER BY date
        ),
        gaps AS (
            SELECT entry_date,
                   CASE
                       WHEN prev_date IS NULL THEN 1
                       WHEN entry_date - prev_date = 1 THEN 0
                       ELSE 1
                   END as gap_flag
            FROM dates
        ),
        groups AS (
            SELECT entry_date,
                   SUM(gap_flag) OVER (ORDER BY entry_date) as group_id
            FROM gaps
        )
        SELECT group_id,
               COUNT(*) as streak_length,
               MIN(entry_date) as start_date,
               MAX(entry_date) as end_date
        FROM groups
        GROUP BY group_id
        ORDER BY streak_length DESC
        LIMIT 1
    """)

    streak_result = session.exec(streak_query).first()

    return {
        'total_entries': result.total_entries,
        'date_range': {
            'first': result.first_entry,
            'last': result.last_entry
        },
        'averages': {
            'mood': round(float(result.avg_mood or 0), 2),
            'pain': round(float(result.avg_pain or 0), 2),
            'energy': round(float(result.avg_energy or 0), 2),
            'sexual_wellbeing': round(float(result.avg_sexual_wellbeing or 0), 2)
        },
        'current_streak': {
            'length': streak_result.streak_length if streak_result else 0,
            'start_date': streak_result.start_date if streak_result else None,
            'end_date': streak_result.end_date if streak_result else None
        } if streak_result else None
    }


@app.get("/export/csv")
def export_all_data_csv(session: Session = Depends(get_session)):
    """Export all health data as CSV for analysis in pandas/excel"""

    # Get all entries ordered by date
    entries = session.exec(
        select(HealthEntry).order_by(HealthEntry.date)
    ).all()

    if not entries:
        raise HTTPException(status_code=404, detail="No data to export")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Define CSV headers - include all fields from your model
    headers = [
        'id', 'date', 'timestamp', 'day_of_week', 'day_name', 'is_weekend',
        'mood', 'pain', 'energy',
        'allergy_state', 'allergy_medication',
        'had_sex', 'sexual_wellbeing', 'sleep_quality',
        'stress_level_work', 'stress_level_home',
        'physical_activity', 'step_count', 'weather_enjoyment',
        'daily_comments'
    ]

    # Add daily_activities columns (flatten the JSON)
    # Get all possible activity keys from the first entry that has activities
    activity_columns = set()
    for entry in entries:
        if entry.daily_activities:
            activity_columns.update(entry.daily_activities.keys())

    # Sort activity columns for consistent ordering
    activity_columns = sorted(activity_columns)
    headers.extend(activity_columns)

    writer.writerow(headers)

    # Write data rows
    for entry in entries:
        row = [
            entry.id,
            entry.date,
            entry.timestamp.isoformat() if entry.timestamp else '',
            entry.day_of_week,
            entry.day_name if hasattr(entry, 'day_name') else '',  # Use computed property
            entry.is_weekend if hasattr(entry, 'is_weekend') else '',  # Use computed property
            entry.mood,
            entry.pain,
            entry.energy,
            entry.allergy_state,
            entry.allergy_medication,
            entry.had_sex,
            entry.sexual_wellbeing,
            entry.sleep_quality,
            entry.stress_level_work,
            entry.stress_level_home,
            entry.physical_activity,
            entry.weather_enjoyment,
            entry.daily_comments or ''  # Handle None values
        ]

        # Add activity columns (1 for present, 0 for absent)
        activities = entry.daily_activities or {}
        for activity in activity_columns:
            row.append(1 if activities.get(activity) == 1 else 0)

        writer.writerow(row)

    # Return as downloadable CSV file
    output.seek(0)
    today = datetime.now().strftime("%Y-%m-%d")

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=health_data_export_{today}.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


@app.get("/export/json")
def export_all_data_json(session: Session = Depends(get_session)):
    """Export all health data as JSON"""

    entries = session.exec(
        select(HealthEntry).order_by(HealthEntry.date)
    ).all()

    if not entries:
        raise HTTPException(status_code=404, detail="No data to export")

    # Convert to list of dicts
    data = []
    for entry in entries:
        entry_dict = entry.dict()
        # Convert datetime to ISO string for JSON serialization
        entry_dict['timestamp'] = entry.timestamp.isoformat() if entry.timestamp else None
        # Add computed properties
        entry_dict['day_name'] = entry.day_name
        entry_dict['is_weekend'] = entry.is_weekend
        data.append(entry_dict)

    today = datetime.now().strftime("%Y-%m-%d")

    return Response(
        content=json.dumps(data, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=health_data_export_{today}.json"
        }
    )