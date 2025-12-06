"""Pytest configuration and shared fixtures."""

import pytest
from datetime import datetime


@pytest.fixture
def minimal_event_data():
    """Minimal valid event data."""
    return {
        "summary": "Test Event",
        "start": datetime(2024, 1, 15, 10, 0, 0),
        "end": datetime(2024, 1, 15, 11, 0, 0),
    }


@pytest.fixture
def complete_event_data():
    """Complete event data with all optional fields."""
    return {
        "summary": "Complete Test Event",
        "start": datetime(2024, 1, 15, 10, 0, 0),
        "end": datetime(2024, 1, 15, 12, 0, 0),
        "description": "A detailed description of the event",
        "location": "Conference Room A",
        "timezone": "America/New_York",
        "organizer": {"name": "Jane Doe", "email": "jane@example.com"},
        "attendees": [
            {"email": "john@example.com", "name": "John Smith", "rsvp": True}
        ],
        "categories": ["Work", "Meeting"],
        "status": "CONFIRMED",
        "priority": 5,
        "url": "https://example.com/event",
    }


@pytest.fixture
def recurring_event_data():
    """Recurring event data."""
    return {
        "summary": "Weekly Meeting",
        "start": datetime(2024, 1, 15, 10, 0, 0),
        "duration": "PT1H",
        "recurrence": {
            "frequency": "WEEKLY",
            "count": 10,
            "by_day": ["MO"],
        },
    }
