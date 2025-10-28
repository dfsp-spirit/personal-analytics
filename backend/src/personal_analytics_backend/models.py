from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer
import calendar
import uuid

class HealthEntryBase(SQLModel):
    uid: str = Field(index=True)  # Add user identifier field
    date: str = Field(index=True, unique=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    day_of_week: Optional[int] = Field(  # Store in DB for querying
        sa_column=Column(Integer),
        ge=0, le=6,  # 0=Monday, 6=Sunday
        description="0=Monday, 1=Tuesday, ..., 6=Sunday"
    )

    # Core metrics
    mood: int = Field(ge=0, le=10)
    pain: int = Field(ge=0, le=10)
    energy: int = Field(ge=0, le=10, default=None)

    # Allergy & Medication
    allergy_state: int = Field(ge=0, le=2)
    allergy_medication: int = Field(ge=0, le=4)

    # Lifestyle
    had_sex: int = Field(ge=0, le=2)
    sexual_wellbeing: int = Field(ge=0, le=10)
    sleep_quality: int = Field(ge=0, le=10)

    # Stress
    stress_level_work: int = Field(ge=0, le=10)
    stress_level_home: int = Field(ge=0, le=10)

    # Optional metrics
    physical_activity: int = Field(ge=0, le=3, default=None)
    step_count: int = Field(ge=0, le=10000, default=None)
    weather_enjoyment: int = Field(ge=0, le=10, default=None)

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
    @property
    def is_weekend(self) -> bool:
        """Convenience property: Saturday=5, Sunday=6"""
        return self.day_of_week >= 5

    @property
    def day_name(self) -> str:
        """Convenience property to get day name"""
        return calendar.day_name[self.day_of_week]


# For API - SQLModel handles serialization automatically
class HealthEntryCreate(HealthEntryBase):
    # Only include fields that the frontend should send
    day_of_week: Optional[int] = None  # Will be computed from date


class HealthEntryRead(HealthEntryBase):
    id: str


class HealthEntryUpdate(SQLModel):
    # All fields optional for updates
    uid: Optional[str] = None
    mood: Optional[int] = None
    pain: Optional[int] = None
    energy: Optional[int] = None
    allergy_state: Optional[int] = None
    allergy_medication: Optional[int] = None
    had_sex: Optional[int] = None
    sexual_wellbeing: Optional[int] = None
    sleep_quality: Optional[int] = None
    stress_level_work: Optional[int] = None
    stress_level_home: Optional[int] = None
    physical_activity: Optional[int] = None
    step_count: Optional[int] = None
    weather_enjoyment: Optional[int] = None
    daily_activities: Optional[Dict[str, Any]] = None
    daily_comments: Optional[str] = None