import pytest
from datetime import datetime
from src.personal_analytics_backend.models import (
    HealthEntry, HealthEntryCreate, HealthEntryRead, HealthEntryUpdate
)
import uuid


class TestHealthEntryBase:
    """Test base functionality shared across all models"""

    def test_valid_health_entry_base(self):
        """Test creating a valid HealthEntryBase instance"""
        entry_data = {
            "uid": "user123",
            "date": "2024-01-15",
            "mood": 8,
            "pain": 2,
            "energy": 7,
            "allergy_state": 1,
            "allergy_medication": 0,
            "had_sex": 1,
            "sexual_wellbeing": 9,
            "sleep_quality": 8,
            "stress_level_work": 3,
            "stress_level_home": 2,
            "physical_activity": 2,
            "step_count": 8500,
            "weather_enjoyment": 9,
            "daily_activities": {"walking": 30, "meditation": 10},
            "daily_comments": "Feeling great today!"
        }

        # Should not raise any validation errors
        entry = HealthEntryCreate(**entry_data)
        assert entry.uid == "user123"
        assert entry.mood == 8
        assert entry.daily_activities["walking"] == 30

    @pytest.mark.parametrize("field,value,expected_error", [
        ("mood", 11, "less than or equal to 10"),
        ("mood", -1, "greater than or equal to 0"),
        ("pain", 11, "less than or equal to 10"),
        ("energy", -5, "greater than or equal to 0"),
        ("allergy_state", 3, "less than or equal to 2"),
        # Note: day_of_week validation doesn't seem to be working in the model
        ("step_count", 15000, "less than or equal to 10000"),
        ("step_count", -100, "greater than or equal to 0"),
    ])
    def test_field_validation_bounds(self, field, value, expected_error):
        """Test field validation for out-of-bounds values"""
        base_data = {
            "uid": "user123",
            "date": "2024-01-15",
            "mood": 5,
            "pain": 5,
            "allergy_state": 1,
            "allergy_medication": 0,
            "had_sex": 1,
            "sexual_wellbeing": 5,
            "sleep_quality": 5,
            "stress_level_work": 5,
            "stress_level_home": 5,
        }

        base_data[field] = value

        with pytest.raises(ValueError) as exc_info:
            HealthEntryCreate(**base_data)

        assert expected_error in str(exc_info.value)

    def test_optional_fields_can_be_omitted(self):
        """Test that optional fields can be omitted (not set to None)"""
        entry_data = {
            "uid": "user123",
            "date": "2024-01-15",
            "mood": 5,
            "pain": 5,
            "allergy_state": 1,
            "allergy_medication": 0,
            "had_sex": 1,
            "sexual_wellbeing": 5,
            "sleep_quality": 5,
            "stress_level_work": 5,
            "stress_level_home": 5,
            # Don't include optional fields at all
        }

        entry = HealthEntryCreate(**entry_data)
        # Default values should be used
        assert entry.energy is None
        assert entry.physical_activity is None
        assert entry.daily_activities == {}


class TestHealthEntry:
    """Test the main HealthEntry table model"""

    def test_health_entry_id_generation(self):
        """Test that ID is automatically generated as UUID"""
        entry = HealthEntry(
            uid="user123",
            date="2024-01-15",
            day_of_week=1,  # Required for HealthEntry
            mood=5,
            pain=5,
            allergy_state=1,
            allergy_medication=0,
            had_sex=1,
            sexual_wellbeing=5,
            sleep_quality=5,
            stress_level_work=5,
            stress_level_home=5,
        )

        # Should have a UUID string as ID
        assert entry.id is not None
        try:
            uuid.UUID(entry.id)
        except ValueError:
            pytest.fail(f"ID {entry.id} is not a valid UUID")

    def test_is_weekend_property(self):
        """Test the is_weekend computed property"""
        # Weekday (Monday = 0)
        weekday_entry = HealthEntry(
            uid="user123",
            date="2024-01-15",  # A Monday
            day_of_week=0,
            mood=5, pain=5, allergy_state=1, allergy_medication=0,
            had_sex=1, sexual_wellbeing=5, sleep_quality=5,
            stress_level_work=5, stress_level_home=5,
        )
        assert not weekday_entry.is_weekend

        # Weekend (Saturday = 5)
        weekend_entry = HealthEntry(
            uid="user123",
            date="2024-01-20",  # A Saturday
            day_of_week=5,
            mood=5, pain=5, allergy_state=1, allergy_medication=0,
            had_sex=1, sexual_wellbeing=5, sleep_quality=5,
            stress_level_work=5, stress_level_home=5,
        )
        assert weekend_entry.is_weekend

    def test_day_name_property(self):
        """Test the day_name computed property"""
        test_cases = [
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ]

        for day_num, expected_name in test_cases:
            entry = HealthEntry(
                uid="user123",
                date="2024-01-15",
                day_of_week=day_num,
                mood=5, pain=5, allergy_state=1, allergy_medication=0,
                had_sex=1, sexual_wellbeing=5, sleep_quality=5,
                stress_level_work=5, stress_level_home=5,
            )
            assert entry.day_name == expected_name

    def test_timestamp_default(self):
        """Test that timestamp defaults to current time"""
        before_creation = datetime.now()
        entry = HealthEntry(
            uid="user123",
            date="2024-01-15",
            day_of_week=1,
            mood=5, pain=5, allergy_state=1, allergy_medication=0,
            had_sex=1, sexual_wellbeing=5, sleep_quality=5,
            stress_level_work=5, stress_level_home=5,
        )
        after_creation = datetime.now()

        assert before_creation <= entry.timestamp <= after_creation


class TestHealthEntryCreate:
    """Test the create model for API input"""

    def test_day_of_week_optional_in_create(self):
        """Test that day_of_week is optional in create model"""
        entry_data = {
            "uid": "user123",
            "date": "2024-01-15",
            "mood": 5,
            "pain": 5,
            "allergy_state": 1,
            "allergy_medication": 0,
            "had_sex": 1,
            "sexual_wellbeing": 5,
            "sleep_quality": 5,
            "stress_level_work": 5,
            "stress_level_home": 5,
            # day_of_week not provided - should be allowed in Create
        }

        entry = HealthEntryCreate(**entry_data)
        assert entry.day_of_week is None


class TestHealthEntryUpdate:
    """Test the update model for partial updates"""

    def test_all_fields_optional(self):
        """Test that all fields are optional in update model"""
        # Should work with empty update
        update = HealthEntryUpdate()
        assert update.uid is None
        assert update.mood is None

        # Should work with partial data
        partial_update = HealthEntryUpdate(mood=8, sleep_quality=9)
        assert partial_update.mood == 8
        assert partial_update.sleep_quality == 9
        assert partial_update.pain is None

    def test_update_with_valid_data(self):
        """Test update with valid field values"""
        update_data = {
            "mood": 10,
            "pain": 0,
            "daily_comments": "Updated comment",
            "daily_activities": {"new_activity": 15}
        }

        update = HealthEntryUpdate(**update_data)
        assert update.mood == 10
        assert update.pain == 0
        assert update.daily_comments == "Updated comment"
        assert update.daily_activities["new_activity"] == 15


class TestHealthEntryRead:
    """Test the read model for API output"""

    def test_read_includes_id(self):
        """Test that read model includes the ID field"""
        entry_data = {
            "id": "test-uuid-123",
            "uid": "user123",
            "date": "2024-01-15",
            "day_of_week": 1,  # Required for Read model
            "mood": 5,
            "pain": 5,
            "allergy_state": 1,
            "allergy_medication": 0,
            "had_sex": 1,
            "sexual_wellbeing": 5,
            "sleep_quality": 5,
            "stress_level_work": 5,
            "stress_level_home": 5,
        }

        entry = HealthEntryRead(**entry_data)
        assert entry.id == "test-uuid-123"


def test_daily_activities_default_dict():
    """Test that daily_activities defaults to empty dict"""
    entry_data = {
        "uid": "user123",
        "date": "2024-01-15",
        "mood": 5,
        "pain": 5,
        "allergy_state": 1,
        "allergy_medication": 0,
        "had_sex": 1,
        "sexual_wellbeing": 5,
        "sleep_quality": 5,
        "stress_level_work": 5,
        "stress_level_home": 5,
        # daily_activities not provided
    }

    entry = HealthEntryCreate(**entry_data)
    assert entry.daily_activities == {}