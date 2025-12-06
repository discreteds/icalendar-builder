"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError

from icalendar_builder.models import (
    Alarm,
    AlarmAction,
    Attendee,
    AttendeeRole,
    CalendarCollection,
    CalendarEvent,
    EventStatus,
    Organizer,
    Recurrence,
    RecurrenceFrequency,
)


class TestCalendarEvent:
    """Tests for CalendarEvent model."""

    def test_minimal_event_with_end(self, minimal_event_data):
        """Test creating minimal event with end datetime."""
        event = CalendarEvent(**minimal_event_data)
        assert event.summary == "Test Event"
        assert event.start == datetime(2024, 1, 15, 10, 0, 0)
        assert event.end == datetime(2024, 1, 15, 11, 0, 0)
        assert event.timezone == "UTC"  # Default

    def test_minimal_event_with_duration(self):
        """Test creating minimal event with duration."""
        event = CalendarEvent(
            summary="Test Event",
            start=datetime(2024, 1, 15, 10, 0, 0),
            duration="PT1H",
        )
        assert event.summary == "Test Event"
        assert event.start == datetime(2024, 1, 15, 10, 0, 0)
        assert event.duration == "PT1H"
        assert event.end is None

    def test_event_requires_summary(self):
        """Test that summary is required."""
        with pytest.raises(PydanticValidationError) as exc_info:
            CalendarEvent(
                start=datetime(2024, 1, 15, 10, 0, 0),
                end=datetime(2024, 1, 15, 11, 0, 0),
            )
        assert "summary" in str(exc_info.value)

    def test_event_requires_start(self):
        """Test that start is required."""
        with pytest.raises(PydanticValidationError) as exc_info:
            CalendarEvent(
                summary="Test",
                end=datetime(2024, 1, 15, 11, 0, 0),
            )
        assert "start" in str(exc_info.value)

    def test_event_requires_end_or_duration(self):
        """Test that either end or duration is required."""
        with pytest.raises(ValueError) as exc_info:
            CalendarEvent(
                summary="Test",
                start=datetime(2024, 1, 15, 10, 0, 0),
            )
        assert "Must specify either 'end' or 'duration'" in str(exc_info.value)

    def test_event_cannot_have_both_end_and_duration(self):
        """Test that event cannot have both end and duration."""
        with pytest.raises(ValueError) as exc_info:
            CalendarEvent(
                summary="Test",
                start=datetime(2024, 1, 15, 10, 0, 0),
                end=datetime(2024, 1, 15, 11, 0, 0),
                duration="PT1H",
            )
        assert "Cannot specify both 'end' and 'duration'" in str(exc_info.value)

    def test_event_validates_datetime_range(self):
        """Test that end must be after start."""
        with pytest.raises(ValueError) as exc_info:
            CalendarEvent(
                summary="Test",
                start=datetime(2024, 1, 15, 11, 0, 0),
                end=datetime(2024, 1, 15, 10, 0, 0),  # Before start!
            )
        assert "must be after start" in str(exc_info.value)

    def test_event_validates_timezone(self):
        """Test that invalid timezone is rejected."""
        with pytest.raises(ValueError) as exc_info:
            CalendarEvent(
                summary="Test",
                start=datetime(2024, 1, 15, 10, 0, 0),
                end=datetime(2024, 1, 15, 11, 0, 0),
                timezone="Invalid/Timezone",
            )
        assert "Invalid timezone" in str(exc_info.value)

    def test_event_accepts_valid_timezone(self):
        """Test that valid timezone is accepted."""
        event = CalendarEvent(
            summary="Test",
            start=datetime(2024, 1, 15, 10, 0, 0),
            end=datetime(2024, 1, 15, 11, 0, 0),
            timezone="Europe/Paris",
        )
        assert event.timezone == "Europe/Paris"

    def test_complete_event(self, complete_event_data):
        """Test creating event with all optional fields."""
        event = CalendarEvent(**complete_event_data)
        assert event.summary == "Complete Test Event"
        assert event.description == "A detailed description of the event"
        assert event.location == "Conference Room A"
        assert event.timezone == "America/New_York"
        assert event.organizer is not None
        assert event.organizer.name == "Jane Doe"
        assert len(event.attendees) == 1
        assert event.categories == ["Work", "Meeting"]
        assert event.status == EventStatus.CONFIRMED
        assert event.priority == 5

    def test_event_with_recurrence(self, recurring_event_data):
        """Test creating recurring event."""
        event = CalendarEvent(**recurring_event_data)
        assert event.recurrence is not None
        assert event.recurrence.frequency == RecurrenceFrequency.WEEKLY
        assert event.recurrence.count == 10
        assert event.recurrence.by_day == ["MO"]


class TestRecurrence:
    """Tests for Recurrence model."""

    def test_recurrence_with_count(self):
        """Test recurrence with count."""
        recurrence = Recurrence(
            frequency=RecurrenceFrequency.WEEKLY,
            count=10,
        )
        assert recurrence.frequency == RecurrenceFrequency.WEEKLY
        assert recurrence.count == 10
        assert recurrence.until is None

    def test_recurrence_with_until(self):
        """Test recurrence with until date."""
        until_date = datetime(2024, 12, 31, 23, 59, 59)
        recurrence = Recurrence(
            frequency=RecurrenceFrequency.DAILY,
            until=until_date,
        )
        assert recurrence.frequency == RecurrenceFrequency.DAILY
        assert recurrence.until == until_date
        assert recurrence.count is None

    def test_recurrence_cannot_have_both_count_and_until(self):
        """Test that recurrence cannot have both count and until."""
        with pytest.raises(ValueError) as exc_info:
            Recurrence(
                frequency=RecurrenceFrequency.WEEKLY,
                count=10,
                until=datetime(2024, 12, 31, 23, 59, 59),
            )
        assert "Cannot specify both count and until" in str(exc_info.value)

    def test_recurrence_validates_by_month_day(self):
        """Test that by_month_day values are validated."""
        with pytest.raises(ValueError) as exc_info:
            Recurrence(
                frequency=RecurrenceFrequency.MONTHLY,
                by_month_day=[1, 15, 32],  # 32 is invalid
            )
        assert "must be 1-31" in str(exc_info.value)


class TestAlarm:
    """Tests for Alarm model."""

    def test_alarm_with_trigger(self):
        """Test creating alarm with trigger."""
        alarm = Alarm(trigger="-PT15M")
        assert alarm.action == AlarmAction.DISPLAY
        assert alarm.trigger == "-PT15M"

    def test_alarm_validates_trigger_format(self):
        """Test that trigger format is validated."""
        with pytest.raises(ValueError) as exc_info:
            Alarm(trigger="15 minutes")  # Invalid format
        assert "ISO 8601 duration" in str(exc_info.value)

    def test_alarm_accepts_various_triggers(self):
        """Test various valid trigger formats."""
        # 15 minutes before
        alarm1 = Alarm(trigger="-PT15M")
        assert alarm1.trigger == "-PT15M"

        # 1 day before
        alarm2 = Alarm(trigger="-P1D")
        assert alarm2.trigger == "-P1D"

        # At event time
        alarm3 = Alarm(trigger="PT0S")
        assert alarm3.trigger == "PT0S"


class TestOrganizer:
    """Tests for Organizer model."""

    def test_organizer_with_name(self):
        """Test creating organizer with name."""
        organizer = Organizer(name="Jane Doe", email="jane@example.com")
        assert organizer.name == "Jane Doe"
        assert organizer.email == "jane@example.com"

    def test_organizer_without_name(self):
        """Test creating organizer without name."""
        organizer = Organizer(email="jane@example.com")
        assert organizer.name is None
        assert organizer.email == "jane@example.com"

    def test_organizer_validates_email(self):
        """Test that email is validated."""
        with pytest.raises(PydanticValidationError):
            Organizer(email="invalid-email")


class TestAttendee:
    """Tests for Attendee model."""

    def test_attendee_defaults(self):
        """Test attendee with default values."""
        attendee = Attendee(email="john@example.com")
        assert attendee.email == "john@example.com"
        assert attendee.name is None
        assert attendee.role == AttendeeRole.REQUIRED
        assert attendee.rsvp is False

    def test_attendee_with_all_fields(self):
        """Test attendee with all fields."""
        attendee = Attendee(
            email="john@example.com",
            name="John Smith",
            role=AttendeeRole.OPTIONAL,
            rsvp=True,
        )
        assert attendee.name == "John Smith"
        assert attendee.role == AttendeeRole.OPTIONAL
        assert attendee.rsvp is True


class TestCalendarCollection:
    """Tests for CalendarCollection model."""

    def test_collection_with_events(self, minimal_event_data):
        """Test creating collection with events."""
        collection = CalendarCollection(
            calendar_name="My Calendar",
            events=[CalendarEvent(**minimal_event_data)],
        )
        assert collection.calendar_name == "My Calendar"
        assert len(collection.events) == 1
        assert collection.timezone == "UTC"

    def test_collection_requires_at_least_one_event(self):
        """Test that collection requires at least one event."""
        with pytest.raises(PydanticValidationError) as exc_info:
            CalendarCollection(
                calendar_name="My Calendar",
                events=[],
            )
        assert "at least 1 item" in str(exc_info.value).lower()

    def test_collection_validates_timezone(self):
        """Test that collection validates timezone."""
        with pytest.raises(ValueError) as exc_info:
            CalendarCollection(
                calendar_name="My Calendar",
                timezone="Invalid/Timezone",
                events=[
                    CalendarEvent(
                        summary="Test",
                        start=datetime(2024, 1, 15, 10, 0, 0),
                        end=datetime(2024, 1, 15, 11, 0, 0),
                    )
                ],
            )
        assert "Invalid timezone" in str(exc_info.value)
