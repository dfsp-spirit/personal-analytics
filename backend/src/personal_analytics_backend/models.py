# backend/src/personal_analytics/models.py
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
import uuid

class HealthEntryBase(SQLModel):
    date: str = Field(index=True, unique=True)  # One entry per day
    timestamp: datetime = Field(default_factory=datetime.now)

    # Core metrics
    mood: int = Field(ge=0, le=10)
    pain: int = Field(ge=0, le=10)
    anxiety: Optional[int] = Field(ge=0, le=10, default=None)
    energy: Optional[int] = Field(ge=0, le=10, default=None)

    # Allergy & Medication
    allergy_state: int = Field(ge=0, le=2)
    allergy_medication: int = Field(ge=0, le=4)

    # Lifestyle
    had_sex: int = Field(ge=0, le=2)
    sleep_quality: int = Field(ge=0, le=10)

    # Stress
    stress_level_work: int = Field(ge=0, le=10)
    stress_level_home: int = Field(ge=0, le=10)

    # Optional metrics
    social_support: Optional[int] = Field(ge=0, le=10, default=None)
    physical_activity: Optional[int] = Field(ge=0, le=3, default=None)
    weather_enjoyment: Optional[int] = Field(ge=0, le=10, default=None)

    # JSONB for flexible activity tracking
    daily_activities: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    daily_comments: Optional[str] = Field(default=None)

class HealthEntry(HealthEntryBase, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )