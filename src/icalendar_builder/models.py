"""Pydantic data models for calendar events and collections."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency options."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class AttendeeRole(str, Enum):
    """Attendee participation roles."""

    REQUIRED = "REQ-PARTICIPANT"
    OPTIONAL = "OPT-PARTICIPANT"
    CHAIR = "CHAIR"
    NON_PARTICIPANT = "NON-PARTICIPANT"


class AlarmAction(str, Enum):
    """Alarm action types."""

    DISPLAY = "DISPLAY"
    EMAIL = "EMAIL"
    AUDIO = "AUDIO"


class EventStatus(str, Enum):
    """Event status values."""

    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Organizer(BaseModel):
    """Event organizer information."""

    name: Optional[str] = None
    email: EmailStr


class Attendee(BaseModel):
    """Event attendee information."""

    email: EmailStr
    name: Optional[str] = None
    role: AttendeeRole = AttendeeRole.REQUIRED
    rsvp: bool = False


class Alarm(BaseModel):
    """Event alarm/reminder configuration."""

    action: AlarmAction = AlarmAction.DISPLAY
    trigger: str = Field(..., description="ISO 8601 duration (e.g., -PT15M)")
    description: Optional[str] = None
    repeat: Optional[int] = Field(None, ge=0)
    duration: Optional[str] = None

    @field_validator("trigger")
    @classmethod
    def validate_trigger(cls, v: str) -> str:
        """Validate trigger format."""
        if not v.startswith(("-P", "P")):
            raise ValueError("Trigger must be ISO 8601 duration (e.g., -PT15M for 15 minutes before)")
        return v


class Recurrence(BaseModel):
    """Recurrence rule configuration."""

    frequency: RecurrenceFrequency
    interval: int = Field(1, ge=1)
    count: Optional[int] = Field(None, ge=1)
    until: Optional[datetime] = None
    by_day: Optional[list[Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]]] = None
    by_month_day: Optional[list[int]] = Field(None)

    @field_validator("by_month_day")
    @classmethod
    def validate_by_month_day(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        """Validate month day values."""
        if v is not None:
            for day in v:
                if day < 1 or day > 31:
                    raise ValueError(f"by_month_day values must be 1-31, got {day}")
        return v

    @model_validator(mode="after")
    def validate_end_condition(self) -> "Recurrence":
        """Ensure either count or until is specified, not both."""
        if self.count and self.until:
            raise ValueError("Cannot specify both count and until in recurrence")
        return self


class CalendarEvent(BaseModel):
    """
    Complete calendar event model.

    This model provides validation and type safety for event data.
    """

    # Required fields
    summary: str = Field(..., min_length=1, max_length=255, description="Event title")
    start: datetime = Field(..., description="Event start datetime")

    # Time specification (one required)
    end: Optional[datetime] = Field(None, description="Event end datetime")
    duration: Optional[str] = Field(None, description="ISO 8601 duration")

    # Optional descriptive fields
    description: Optional[str] = Field(None, description="Detailed event description")
    location: Optional[str] = Field(None, description="Event location")

    # Timezone
    timezone: str = Field(default="UTC", description="IANA timezone identifier")

    # Unique identifier
    uid: Optional[str] = Field(None, description="Unique event ID (auto-generated if not provided)")

    # People
    organizer: Optional[Organizer] = Field(None, description="Event organizer")
    attendees: list[Attendee] = Field(default_factory=list, description="Event attendees")

    # Recurrence
    recurrence: Optional[Recurrence] = Field(None, description="Recurrence rule")

    # Alarms
    alarms: list[Alarm] = Field(default_factory=list, description="Event reminders")

    # Categorization
    categories: list[str] = Field(default_factory=list, description="Event categories/tags")

    # Status and properties
    status: EventStatus = Field(default=EventStatus.CONFIRMED)
    transparency: Literal["OPAQUE", "TRANSPARENT"] = Field(default="OPAQUE")
    priority: int = Field(default=0, ge=0, le=9)
    url: Optional[str] = Field(None, description="Associated URL")

    # Custom properties
    custom_properties: dict[str, str] = Field(
        default_factory=dict, description="Custom X-properties for extensibility"
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate IANA timezone name."""
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(v)
        except Exception as e:
            raise ValueError(
                f"Invalid timezone: {v}. Use IANA timezone names like 'UTC', "
                f"'Europe/Paris', 'America/New_York'. Error: {e}"
            )
        return v

    @model_validator(mode="after")
    def validate_time_specification(self) -> "CalendarEvent":
        """Ensure either end or duration is specified, not both."""
        if not self.end and not self.duration:
            raise ValueError("Must specify either 'end' or 'duration'")
        if self.end and self.duration:
            raise ValueError("Cannot specify both 'end' and 'duration'")
        return self

    @model_validator(mode="after")
    def validate_datetime_range(self) -> "CalendarEvent":
        """Ensure end datetime is after start datetime."""
        if self.end and self.end <= self.start:
            raise ValueError(
                f"Event end ({self.end}) must be after start ({self.start})"
            )
        return self


class CalendarCollection(BaseModel):
    """
    Collection of events forming a calendar.

    This model is used when loading calendars from JSON files.
    """

    calendar_name: str = Field(..., description="Calendar name")
    calendar_description: Optional[str] = Field(None, description="Calendar description")
    product_id: str = Field(default="//icalendar-builder//EN", description="PRODID")
    timezone: str = Field(default="UTC", description="Default timezone for events")
    method: Optional[Literal["PUBLISH", "REQUEST", "REPLY", "ADD", "CANCEL", "REFRESH"]] = None
    events: list[CalendarEvent] = Field(..., min_length=1, description="Event list")

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate IANA timezone name."""
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(v)
        except Exception as e:
            raise ValueError(
                f"Invalid timezone: {v}. Use IANA timezone names like 'UTC', "
                f"'Europe/Paris', 'America/New_York'. Error: {e}"
            )
        return v
