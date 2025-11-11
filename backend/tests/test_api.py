import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock
from datetime import datetime
from sqlmodel import select

from src.personal_analytics_backend.api import app
from src.personal_analytics_backend.models import HealthEntry
from src.personal_analytics_backend.database import get_session


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Mock database session with proper chaining"""
    session = Mock()

    # Create a mock that returns itself for method chaining
    chain_mock = Mock()
    chain_mock.where.return_value = chain_mock
    chain_mock.order_by.return_value = chain_mock
    chain_mock.offset.return_value = chain_mock
    chain_mock.limit.return_value = chain_mock

    # Set the final return values
    chain_mock.first.return_value = None
    chain_mock.all.return_value = []

    # session.exec returns our chainable mock
    session.exec.return_value = chain_mock

    return session


@pytest.fixture
def sample_health_entry():
    """Sample HealthEntry object"""
    return HealthEntry(
        id="test-uuid-123",
        uid="user123",
        date="2024-01-15",
        day_of_week=1,
        timestamp=datetime.now(),
        mood=8,
        pain=2,
        energy=7,
        allergy_state=1,
        allergy_medication=0,
        had_sex=1,
        sexual_wellbeing=9,
        sleep_quality=8,
        stress_level_work=3,
        stress_level_home=2,
        physical_activity=2,
        step_count=8500,
        weather_enjoyment=9,
    )


def test_get_specific_entry_success(client, mock_session, sample_health_entry):
    """Test getting a specific entry by ID"""

    # Setup mock - return our sample entry for .first() call
    mock_session.exec.return_value.first.return_value = sample_health_entry

    # Override the dependency for this test
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        # Make the request
        response = client.get("/entries/test-uuid-123")

        # Debug output
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "test-uuid-123"
        assert data["uid"] == "user123"

        # Verify mock was called
        mock_session.exec.assert_called_once()

    finally:
        # Clean up
        app.dependency_overrides.clear()


def test_get_specific_entry_not_found(client, mock_session):
    """Test getting a non-existent entry"""

    # Setup mock - return None for not found
    mock_session.exec.return_value.first.return_value = None

    # Override the dependency
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get("/entries/nonexistent-id")

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify the query was executed
        mock_session.exec.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_get_all_entries_basic(client, mock_session, sample_health_entry):
    """Test basic get all entries endpoint"""

    # Setup mock - return our sample entry for .all() call
    mock_session.exec.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_health_entry]

    # Override dependency
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get("/entries/?uid=user123")

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["uid"] == "user123"

    finally:
        app.dependency_overrides.clear()


def test_get_all_entries_empty(client, mock_session):
    """Test get all entries when no data exists"""

    # Setup mock - return empty list
    mock_session.exec.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    # Override dependency
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get("/entries/?uid=user123")

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    finally:
        app.dependency_overrides.clear()


# Let's also test a simpler endpoint to verify our mocking works
def test_health_check_endpoint(client, mock_session):
    """Test health check endpoint with mocking"""

    # Mock some entries for the health check
    mock_entries = [Mock(), Mock(), Mock()]  # 3 mock entries
    mock_session.exec.return_value.all.return_value = mock_entries

    # Override dependency
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get("/health")

        print(f"Health check response status: {response.status_code}")
        print(f"Health check content: {response.text}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        # The health endpoint counts entries, so it should see our 3 mock entries
        assert data["entries_count"] == 3

    finally:
        app.dependency_overrides.clear()