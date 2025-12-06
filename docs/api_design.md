# ICalendar Builder - API Design

## Document Information

**Version:** 1.0
**Date:** 2025-01-01
**Status:** Draft

## 1. API Overview

### 1.1 Design Philosophy

The ICalendar Builder API is designed for **orchestration software** with these principles:

1. **Simple for Simple Tasks**: Common operations require minimal code
2. **Powerful for Complex Tasks**: Advanced features available when needed
3. **Type-Safe**: Full type hints for IDE autocomplete and type checking
4. **Explicit over Implicit**: Clear, predictable behavior
5. **Fail Fast**: Validation errors raised early with clear messages

### 1.2 Import Structure

```python
# Primary imports for most use cases
from icalendar_builder import CalendarBuilder, CalendarEvent

# Extended imports for advanced usage
from icalendar_builder import (
    CalendarBuilder,
    CalendarEvent,
    CalendarCollection,
    EventFactory,
    Organizer,
    Attendee,
    Alarm,
    Recurrence,
)

# Exception handling
from icalendar_builder import (
    ValidationError,
    TemplateError,
    TimezoneError,
)
```

---

## 2. CalendarBuilder Class

### 2.1 Class Definition

```python
class CalendarBuilder:
    """
    Main interface for building ICS calendar files.

    This class provides a fluent API for creating calendars from event data.
    It supports loading from JSON/dict, programmatic event addition,
    and generation of both combined and individual event files.

    Examples:
        Simple usage:
        >>> builder = CalendarBuilder(timezone="Europe/Paris")
        >>> builder.add_event(
        ...     summary="Team Meeting",
        ...     start="2024-01-15T10:00:00",
        ...     end="2024-01-15T11:00:00"
        ... )
        >>> builder.save("meeting.ics")

        From JSON:
        >>> CalendarBuilder.from_json("events.json").save("calendar.ics")

        Method chaining:
        >>> (CalendarBuilder()
        ...     .add_event(summary="Event 1", start=..., end=...)
        ...     .add_event(summary="Event 2", start=..., end=...)
        ...     .save("calendar.ics"))
    """

    def __init__(
        self,
        calendar_name: str = "My Calendar",
        timezone: str = "UTC",
        template: str = "standard",
        validate: bool = True
    ) -> None:
        """
        Initialize calendar builder.

        Args:
            calendar_name: Name of the calendar (appears in calendar apps)
            timezone: Default IANA timezone for all events
            template: Template name ("standard", "sport", "music", "recurring")
                     or path to custom template file
            validate: Whether to validate generated ICS for RFC 5545 compliance

        Raises:
            TimezoneError: If timezone is not a valid IANA identifier

        Example:
            >>> builder = CalendarBuilder(
            ...     calendar_name="Tour de France 2024",
            ...     timezone="Europe/Paris",
            ...     template="sport",
            ...     validate=True
            ... )
        """
```

### 2.2 Adding Events

#### 2.2.1 add_event()

```python
def add_event(
    self,
    summary: str,
    start: Union[str, datetime],
    end: Optional[Union[str, datetime]] = None,
    duration: Optional[str] = None,
    **kwargs
) -> 'CalendarBuilder':
    """
    Add an event to the calendar.

    Args:
        summary: Event title/summary (required)
        start: Start datetime as ISO 8601 string or datetime object (required)
        end: End datetime (required if duration not provided)
        duration: ISO 8601 duration string (required if end not provided)
        **kwargs: Additional event properties:
            - description (str): Detailed event description
            - location (str): Event location
            - timezone (str): Override default timezone for this event
            - uid (str): Unique identifier (auto-generated if not provided)
            - organizer (dict): {"name": str, "email": str}
            - attendees (list[dict]): List of attendee dicts
            - categories (list[str]): Event categories/tags
            - status (str): "TENTATIVE", "CONFIRMED", or "CANCELLED"
            - priority (int): Priority 0-9 (0=undefined, 1=highest)
            - url (str): Associated URL
            - transparency (str): "OPAQUE" or "TRANSPARENT"
            - custom_properties (dict[str, str]): Custom X-properties

    Returns:
        Self for method chaining

    Raises:
        ValidationError: If event data is invalid

    Examples:
        Minimal event:
        >>> builder.add_event(
        ...     summary="Team Meeting",
        ...     start="2024-01-15T10:00:00",
        ...     duration="PT1H"
        ... )

        Complete event:
        >>> builder.add_event(
        ...     summary="Project Kickoff",
        ...     start="2024-01-15T10:00:00",
        ...     end="2024-01-15T12:00:00",
        ...     description="Kickoff meeting for Q1 project",
        ...     location="Conference Room A",
        ...     organizer={"name": "Jane Doe", "email": "jane@example.com"},
        ...     attendees=[
        ...         {"email": "john@example.com", "name": "John Smith", "rsvp": True}
        ...     ],
        ...     categories=["Work", "Meeting"],
        ...     status="CONFIRMED",
        ...     priority=5,
        ...     url="https://example.com/meeting-details"
        ... )

        With custom properties:
        >>> builder.add_event(
        ...     summary="Tour de France Stage 1",
        ...     start="2024-06-29T09:00:00",
        ...     end="2024-06-29T17:00:00",
        ...     custom_properties={
        ...         "X-SPORT-TYPE": "Cycling",
        ...         "X-STAGE-NUMBER": "1",
        ...         "X-DISTANCE": "205km"
        ...     }
        ... )
    """
```

#### 2.2.2 add_events()

```python
def add_events(self, events: list[dict]) -> 'CalendarBuilder':
    """
    Add multiple events from a list of dictionaries.

    Args:
        events: List of event dictionaries with same structure as add_event kwargs

    Returns:
        Self for method chaining

    Raises:
        ValidationError: If any event data is invalid

    Example:
        >>> events = [
        ...     {
        ...         "summary": "Event 1",
        ...         "start": "2024-01-15T10:00:00",
        ...         "end": "2024-01-15T11:00:00"
        ...     },
        ...     {
        ...         "summary": "Event 2",
        ...         "start": "2024-01-16T10:00:00",
        ...         "duration": "PT2H"
        ...     }
        ... ]
        >>> builder.add_events(events)
    """
```

### 2.3 Loading Data

#### 2.3.1 from_json()

```python
@classmethod
def from_json(cls, json_path: Union[str, Path]) -> 'CalendarBuilder':
    """
    Create builder from JSON file.

    The JSON file should contain a CalendarCollection with calendar metadata
    and an array of events.

    Args:
        json_path: Path to JSON file

    Returns:
        CalendarBuilder instance with events loaded

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        ValidationError: If JSON structure is invalid

    Example:
        JSON file (events.json):
        {
          "calendar_name": "My Events",
          "timezone": "Europe/Paris",
          "events": [
            {
              "summary": "Event 1",
              "start": "2024-06-29T09:00:00",
              "end": "2024-06-29T17:00:00"
            }
          ]
        }

        Usage:
        >>> builder = CalendarBuilder.from_json("events.json")
        >>> builder.save("output.ics")
    """
```

#### 2.3.2 from_dict()

```python
@classmethod
def from_dict(cls, data: dict) -> 'CalendarBuilder':
    """
    Create builder from dictionary.

    Args:
        data: Dictionary with CalendarCollection structure

    Returns:
        CalendarBuilder instance with events loaded

    Raises:
        ValidationError: If data structure is invalid

    Example:
        >>> data = {
        ...     "calendar_name": "My Calendar",
        ...     "timezone": "UTC",
        ...     "events": [
        ...         {
        ...             "summary": "Event 1",
        ...             "start": "2024-01-15T10:00:00",
        ...             "duration": "PT1H"
        ...         }
        ...     ]
        ... }
        >>> builder = CalendarBuilder.from_dict(data)
    """
```

### 2.4 Generating Output

#### 2.4.1 generate()

```python
def generate(self) -> str:
    """
    Generate ICS calendar content as string.

    This method renders all events using the configured template and
    assembles them into a complete VCALENDAR structure.

    Returns:
        ICS file content as string

    Raises:
        ValidationError: If validation enabled and ICS is invalid
        TemplateError: If template rendering fails
        GenerationError: If ICS generation fails

    Example:
        >>> content = builder.generate()
        >>> print(content[:100])
        BEGIN:VCALENDAR
        VERSION:2.0
        PRODID://icalendar-builder//EN
        ...
    """
```

#### 2.4.2 save()

```python
def save(self, output_path: Union[str, Path]) -> Path:
    """
    Save calendar to ICS file.

    Creates parent directories if they don't exist.
    Generates and validates ICS content, then writes to file.

    Args:
        output_path: Output file path (with .ics extension)

    Returns:
        Path object pointing to saved file

    Raises:
        ValidationError: If validation enabled and ICS is invalid
        IOError: If file cannot be written

    Example:
        >>> output_file = builder.save("calendars/my_events.ics")
        >>> print(f"Saved to: {output_file}")
        Saved to: calendars/my_events.ics
    """
```

#### 2.4.3 save_individual_events()

```python
def save_individual_events(
    self,
    output_dir: Union[str, Path],
    filename_template: str = "event_{index}.ics"
) -> list[Path]:
    """
    Save each event as a separate ICS file.

    Useful for generating individual calendar invitations or
    allowing selective import of events.

    Args:
        output_dir: Directory for output files
        filename_template: Template for filenames with placeholders:
            - {index}: Event number (1-based)
            - {summary}: Event summary (sanitized for filesystem)

    Returns:
        List of Path objects for all created files

    Raises:
        IOError: If files cannot be written

    Example:
        Default naming:
        >>> files = builder.save_individual_events("events/")
        >>> print(files)
        [Path('events/event_1.ics'), Path('events/event_2.ics'), ...]

        Custom naming with summary:
        >>> files = builder.save_individual_events(
        ...     "events/",
        ...     filename_template="{index:03d}_{summary}.ics"
        ... )
        >>> print(files)
        [Path('events/001_Team_Meeting.ics'), ...]
    """
```

### 2.5 Utility Methods

#### 2.5.1 clear_events()

```python
def clear_events(self) -> 'CalendarBuilder':
    """
    Remove all events from the builder.

    Returns:
        Self for method chaining

    Example:
        >>> builder.add_event(...)
        >>> builder.clear_events()
        >>> len(builder)
        0
    """
```

#### 2.5.2 __len__()

```python
def __len__(self) -> int:
    """
    Return number of events in the builder.

    Example:
        >>> builder = CalendarBuilder()
        >>> len(builder)
        0
        >>> builder.add_event(summary="Event", start="2024-01-15T10:00:00", duration="PT1H")
        >>> len(builder)
        1
    """
```

#### 2.5.3 __repr__()

```python
def __repr__(self) -> str:
    """
    String representation of builder.

    Example:
        >>> builder = CalendarBuilder(calendar_name="My Cal")
        >>> builder.add_event(...)
        >>> print(builder)
        CalendarBuilder(name='My Cal', events=1)
    """
```

---

## 3. EventFactory Class

### 3.1 Class Definition

```python
class EventFactory:
    """
    Factory for creating common event types with sensible defaults.

    This class provides convenient methods for creating events with
    pre-configured settings for common use cases like sports, music,
    and meetings.
    """
```

### 3.2 Factory Methods

#### 3.2.1 sport_event()

```python
@staticmethod
def sport_event(
    sport_name: str,
    event_name: str,
    start: datetime,
    duration: str = "PT2H",
    location: Optional[str] = None,
    **kwargs
) -> CalendarEvent:
    """
    Create a sports event with appropriate defaults.

    Args:
        sport_name: Name of the sport (e.g., "Cycling", "Football")
        event_name: Specific event description (e.g., "Stage 1", "Final")
        start: Event start datetime
        duration: ISO 8601 duration (default: 2 hours)
        location: Event location
        **kwargs: Additional event properties

    Returns:
        CalendarEvent model

    Example:
        >>> event = EventFactory.sport_event(
        ...     sport_name="Cycling",
        ...     event_name="Tour de France Stage 1",
        ...     start=datetime(2024, 6, 29, 9, 0),
        ...     duration="PT8H",
        ...     location="Florence, Italy"
        ... )
        >>> builder.add_event(**event.model_dump())

    Generated event includes:
        - Summary: "{sport_name} - {event_name}"
        - Categories: ["Sports", sport_name]
        - Custom property: X-SPORT-TYPE
    """
```

#### 3.2.2 music_event()

```python
@staticmethod
def music_event(
    artist: str,
    venue: str,
    start: datetime,
    end: datetime,
    ticket_url: Optional[str] = None,
    **kwargs
) -> CalendarEvent:
    """
    Create a music/concert event with appropriate defaults.

    Args:
        artist: Artist or band name
        venue: Concert venue
        start: Event start datetime
        end: Event end datetime
        ticket_url: URL for ticket information
        **kwargs: Additional event properties

    Returns:
        CalendarEvent model

    Example:
        >>> event = EventFactory.music_event(
        ...     artist="The Band",
        ...     venue="Madison Square Garden",
        ...     start=datetime(2024, 7, 15, 20, 0),
        ...     end=datetime(2024, 7, 15, 23, 0),
        ...     ticket_url="https://tickets.example.com/the-band"
        ... )

    Generated event includes:
        - Summary: artist name
        - Location: venue
        - Categories: ["Music", "Concert"]
        - Alarm: 15 minutes before (DISPLAY)
        - URL: ticket_url if provided
    """
```

#### 3.2.3 recurring_meeting()

```python
@staticmethod
def recurring_meeting(
    summary: str,
    start: datetime,
    duration: str,
    frequency: RecurrenceFrequency,
    count: Optional[int] = None,
    until: Optional[datetime] = None,
    by_day: Optional[list[str]] = None,
    **kwargs
) -> CalendarEvent:
    """
    Create a recurring meeting event.

    Args:
        summary: Meeting title
        start: First occurrence start datetime
        duration: Meeting duration (ISO 8601)
        frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY, YEARLY)
        count: Number of occurrences (optional)
        until: Recurrence end date (optional)
        by_day: Days of week for recurrence (e.g., ["MO", "WE", "FR"])
        **kwargs: Additional event properties

    Returns:
        CalendarEvent model

    Example:
        Weekly standup for 12 weeks:
        >>> event = EventFactory.recurring_meeting(
        ...     summary="Team Standup",
        ...     start=datetime(2024, 1, 15, 9, 0),
        ...     duration="PT15M",
        ...     frequency=RecurrenceFrequency.WEEKLY,
        ...     count=12,
        ...     by_day=["MO", "WE", "FR"]
        ... )

    Generated event includes:
        - Recurrence rule configured
        - Categories: ["Meeting"]
        - Alarm: 5 minutes before
    """
```

#### 3.2.4 all_day_event()

```python
@staticmethod
def all_day_event(
    summary: str,
    date: Union[str, date],
    location: Optional[str] = None,
    **kwargs
) -> CalendarEvent:
    """
    Create an all-day event.

    Args:
        summary: Event title
        date: Event date (YYYY-MM-DD string or date object)
        location: Event location
        **kwargs: Additional event properties

    Returns:
        CalendarEvent model

    Example:
        >>> event = EventFactory.all_day_event(
        ...     summary="Company Holiday",
        ...     date="2024-12-25",
        ...     categories=["Holiday"]
        ... )

    Generated event:
        - Start: date at 00:00:00
        - Duration: P1D (24 hours)
        - Transparency: TRANSPARENT (doesn't block time)
    """
```

---

## 4. Data Models

### 4.1 CalendarEvent Model

```python
class CalendarEvent(BaseModel):
    """
    Pydantic model representing a calendar event.

    This model provides validation and type safety for event data.
    It can be used directly for programmatic event creation or
    loaded from JSON/dict.

    All fields use type hints for IDE autocomplete and type checking.
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
    uid: Optional[str] = Field(None, description="Unique event ID (auto-generated)")

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
        default_factory=dict,
        description="Custom X-properties for extensibility"
    )

    # Validation
    @model_validator(mode='after')
    def validate_time_specification(self):
        """Ensure either end or duration is specified, not both."""
        if not self.end and not self.duration:
            raise ValueError("Must specify either 'end' or 'duration'")
        if self.end and self.duration:
            raise ValueError("Cannot specify both 'end' and 'duration'")
        return self
```

### 4.2 CalendarCollection Model

```python
class CalendarCollection(BaseModel):
    """
    Pydantic model for a collection of events forming a calendar.

    This model is used when loading calendars from JSON files.
    """

    calendar_name: str = Field(..., description="Calendar name")
    calendar_description: Optional[str] = Field(None, description="Calendar description")
    product_id: str = Field(default="//icalendar-builder//EN", description="PRODID")
    timezone: str = Field(default="UTC", description="Default timezone for events")
    method: Optional[Literal["PUBLISH", "REQUEST", "REPLY", "ADD", "CANCEL", "REFRESH"]] = None
    events: list[CalendarEvent] = Field(..., min_length=1, description="Event list")
```

### 4.3 Supporting Models

```python
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

class Recurrence(BaseModel):
    """Recurrence rule configuration."""
    frequency: RecurrenceFrequency
    interval: int = Field(1, ge=1)
    count: Optional[int] = Field(None, ge=1)
    until: Optional[datetime] = None
    by_day: Optional[list[Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]]] = None
    by_month_day: Optional[list[int]] = Field(None, ge=1, le=31)
```

---

## 5. Exception Classes

### 5.1 Exception Hierarchy

```python
class ICSBuilderError(Exception):
    """Base exception for all icalendar-builder errors."""
    pass

class ValidationError(ICSBuilderError):
    """
    Data validation failed.

    Attributes:
        field: Name of the field that failed validation (if applicable)
        message: Error message describing the validation failure
    """
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message)

class TemplateError(ICSBuilderError):
    """Template rendering or loading failed."""
    pass

class TimezoneError(ICSBuilderError):
    """
    Invalid or unsupported timezone.

    Attributes:
        timezone: The invalid timezone string
        message: Error message with details
    """
    def __init__(self, timezone: str, message: Optional[str] = None):
        self.timezone = timezone
        msg = message or f"Invalid timezone: {timezone}"
        super().__init__(msg)

class GenerationError(ICSBuilderError):
    """ICS file generation failed."""
    pass

class FileIOError(ICSBuilderError):
    """
    File I/O operation failed.

    Attributes:
        path: Path to the file
        operation: Operation being performed (read, write, etc.)
        original_error: The underlying exception
    """
    def __init__(self, path: Path, operation: str, original_error: Exception):
        self.path = path
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Failed to {operation} file {path}: {original_error}")
```

---

## 6. Usage Examples

### 6.1 Basic Usage

```python
from icalendar_builder import CalendarBuilder

# Simple calendar with one event
builder = CalendarBuilder(
    calendar_name="My Calendar",
    timezone="Australia/Melbourne"
)

builder.add_event(
    summary="Team Meeting",
    start="2024-01-15T10:00:00",
    end="2024-01-15T11:00:00",
    location="Conference Room A"
)

builder.save("meeting.ics")
```

### 6.2 Method Chaining

```python
from icalendar_builder import CalendarBuilder

(CalendarBuilder(timezone="Europe/Paris")
    .add_event(
        summary="Morning Standup",
        start="2024-01-15T09:00:00",
        duration="PT15M"
    )
    .add_event(
        summary="Lunch Break",
        start="2024-01-15T12:00:00",
        duration="PT1H"
    )
    .add_event(
        summary="Afternoon Review",
        start="2024-01-15T16:00:00",
        duration="PT30M"
    )
    .save("daily_schedule.ics"))
```

### 6.3 Loading from JSON

```python
from icalendar_builder import CalendarBuilder

# JSON file: events.json
# {
#   "calendar_name": "Tour de France 2024",
#   "timezone": "Europe/Paris",
#   "events": [
#     {
#       "summary": "Stage 1: Florence – Rimini",
#       "start": "2024-06-29T09:00:00",
#       "end": "2024-06-29T17:00:00",
#       "description": "205 km, hills",
#       "categories": ["Sports", "Cycling"]
#     },
#     {
#       "summary": "Stage 2: Cesenatico – Bologna",
#       "start": "2024-06-30T09:00:00",
#       "end": "2024-06-30T17:00:00"
#     }
#   ]
# }

# Load and generate
CalendarBuilder.from_json("events.json").save("tdf_2024.ics")

# Or with modifications
builder = CalendarBuilder.from_json("events.json")
builder.template = "sport"  # Use sport template
builder.add_event(  # Add one more event
    summary="Stage 3",
    start="2024-07-01T09:00:00",
    duration="PT8H"
)
builder.save("tdf_2024.ics")
```

### 6.4 Using EventFactory

```python
from icalendar_builder import CalendarBuilder, EventFactory
from icalendar_builder.models import RecurrenceFrequency
from datetime import datetime

builder = CalendarBuilder(timezone="America/New_York")

# Sports event
sport_event = EventFactory.sport_event(
    sport_name="Basketball",
    event_name="Finals Game 1",
    start=datetime(2024, 6, 6, 20, 30),
    duration="PT3H",
    location="Madison Square Garden"
)
builder.add_event(**sport_event.model_dump())

# Music event
music_event = EventFactory.music_event(
    artist="Taylor Swift",
    venue="MetLife Stadium",
    start=datetime(2024, 8, 15, 19, 0),
    end=datetime(2024, 8, 15, 23, 0),
    ticket_url="https://tickets.example.com"
)
builder.add_event(**music_event.model_dump())

# Recurring meeting
meeting = EventFactory.recurring_meeting(
    summary="Weekly Team Sync",
    start=datetime(2024, 1, 8, 10, 0),  # Monday
    duration="PT30M",
    frequency=RecurrenceFrequency.WEEKLY,
    count=12,
    by_day=["MO"]
)
builder.add_event(**meeting.model_dump())

builder.save("mixed_events.ics")
```

### 6.5 Individual Event Files

```python
from icalendar_builder import CalendarBuilder

# Create calendar with multiple events
builder = CalendarBuilder.from_json("festival_events.json")

# Save as combined calendar
builder.save("festival_combined.ics")

# Also save individual event files
individual_files = builder.save_individual_events(
    output_dir="festival_events/",
    filename_template="{index:02d}_{summary}.ics"
)

print(f"Created {len(individual_files)} individual event files")
for file in individual_files:
    print(f"  - {file.name}")

# Output:
# Created 10 individual event files
#   - 01_Opening_Ceremony.ics
#   - 02_Main_Stage_Day_1.ics
#   - 03_Acoustic_Tent_Day_1.ics
#   ...
```

### 6.6 Advanced Event with All Features

```python
from icalendar_builder import CalendarBuilder
from datetime import datetime

builder = CalendarBuilder(timezone="Europe/London")

builder.add_event(
    summary="Annual Conference 2024",
    start="2024-09-15T09:00:00",
    end="2024-09-15T17:00:00",
    description=(
        "Annual company conference featuring:\n"
        "- Keynote speeches\n"
        "- Breakout sessions\n"
        "- Networking lunch\n"
        "- Awards ceremony"
    ),
    location="London Convention Centre, Hall A",
    organizer={
        "name": "Events Team",
        "email": "events@company.com"
    },
    attendees=[
        {
            "email": "john@company.com",
            "name": "John Smith",
            "role": "REQ-PARTICIPANT",
            "rsvp": True
        },
        {
            "email": "jane@company.com",
            "name": "Jane Doe",
            "role": "OPT-PARTICIPANT",
            "rsvp": False
        }
    ],
    alarms=[
        {
            "action": "DISPLAY",
            "trigger": "-P1D",  # 1 day before
            "description": "Conference tomorrow!"
        },
        {
            "action": "DISPLAY",
            "trigger": "-PT1H",  # 1 hour before
            "description": "Conference starts in 1 hour"
        }
    ],
    categories=["Conference", "Company Event"],
    status="CONFIRMED",
    priority=5,
    url="https://conference.company.com/2024",
    transparency="OPAQUE",
    custom_properties={
        "X-CONFERENCE-TRACK": "Leadership",
        "X-REQUIRES-REGISTRATION": "TRUE",
        "X-DRESS-CODE": "Business Casual"
    }
)

builder.save("conference_2024.ics")
```

### 6.7 Recurring Events

```python
from icalendar_builder import CalendarBuilder
from datetime import datetime

builder = CalendarBuilder(timezone="UTC")

# Daily standup for 5 weeks
builder.add_event(
    summary="Daily Standup",
    start="2024-01-15T09:00:00",
    duration="PT15M",
    recurrence={
        "frequency": "DAILY",
        "count": 25,  # 5 weeks * 5 days
        "by_day": ["MO", "TU", "WE", "TH", "FR"]
    },
    location="Zoom Room 1"
)

# Monthly board meeting on first Monday
builder.add_event(
    summary="Board Meeting",
    start="2024-01-01T14:00:00",
    duration="PT2H",
    recurrence={
        "frequency": "MONTHLY",
        "by_day": ["1MO"],  # First Monday
        "count": 12  # All year
    },
    location="Boardroom"
)

# Weekly team lunch every Friday until end of quarter
builder.add_event(
    summary="Team Lunch",
    start="2024-01-05T12:00:00",
    duration="PT1H",
    recurrence={
        "frequency": "WEEKLY",
        "by_day": ["FR"],
        "until": "2024-03-31T23:59:59"
    },
    location="Local Restaurant"
)

builder.save("recurring_events.ics")
```

### 6.8 Error Handling

```python
from icalendar_builder import CalendarBuilder, ValidationError, TimezoneError

try:
    builder = CalendarBuilder(timezone="Invalid/Timezone")
except TimezoneError as e:
    print(f"Invalid timezone: {e.timezone}")
    # Use default
    builder = CalendarBuilder()

try:
    builder.add_event(
        summary="",  # Invalid: empty summary
        start="2024-01-15T10:00:00",
        duration="PT1H"
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    if e.field:
        print(f"  Field: {e.field}")

try:
    builder.add_event(
        summary="Invalid Event",
        start="2024-01-15T10:00:00",
        end="2024-01-15T09:00:00"  # End before start!
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### 6.9 Programmatic Generation for Orchestration

```python
from icalendar_builder import CalendarBuilder
from datetime import datetime, timedelta

def generate_event_series(
    base_date: datetime,
    event_template: dict,
    count: int
) -> None:
    """
    Generate a series of events for orchestration pipeline.

    This function demonstrates how orchestration software
    might use icalendar-builder to generate calendars
    from computed data.
    """
    builder = CalendarBuilder(
        calendar_name=event_template["calendar_name"],
        timezone=event_template["timezone"],
        template=event_template.get("template", "standard")
    )

    for i in range(count):
        event_date = base_date + timedelta(days=i)

        builder.add_event(
            summary=f"{event_template['summary']} - Day {i+1}",
            start=event_date.isoformat(),
            duration=event_template["duration"],
            description=event_template.get("description", ""),
            location=event_template.get("location"),
            categories=event_template.get("categories", [])
        )

    output_path = event_template["output_path"]
    builder.save(output_path)

    print(f"Generated {count} events → {output_path}")


# Usage in orchestration pipeline
event_config = {
    "calendar_name": "Tour de France 2024",
    "timezone": "Europe/Paris",
    "template": "sport",
    "summary": "Stage",
    "duration": "PT6H",
    "description": "Tour de France stage",
    "categories": ["Sports", "Cycling"],
    "output_path": "/output/tdf_2024.ics"
}

generate_event_series(
    base_date=datetime(2024, 6, 29, 9, 0),
    event_template=event_config,
    count=21  # 21 stages
)
```

### 6.10 Batch Processing

```python
from icalendar_builder import CalendarBuilder
import json
from pathlib import Path

def batch_generate_calendars(config_dir: Path, output_dir: Path) -> None:
    """
    Batch generate multiple calendars from JSON configurations.

    Useful for orchestration systems that need to generate
    many calendars in one run.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for config_file in config_dir.glob("*.json"):
        try:
            print(f"Processing {config_file.name}...")

            # Load and generate
            builder = CalendarBuilder.from_json(config_file)

            # Output filename based on calendar name
            safe_name = builder.calendar_name.replace(" ", "_").lower()
            output_file = output_dir / f"{safe_name}.ics"

            builder.save(output_file)

            print(f"  ✓ Generated {output_file.name} ({len(builder)} events)")

        except Exception as e:
            print(f"  ✗ Error: {e}")


# Usage
batch_generate_calendars(
    config_dir=Path("/config/calendars"),
    output_dir=Path("/output/calendars")
)

# Output:
# Processing tdf_2024.json...
#   ✓ Generated tour_de_france_2024.ics (21 events)
# Processing festival.json...
#   ✓ Generated golden_plains_2024.ics (30 events)
# Processing meetings.json...
#   ✓ Generated recurring_meetings.ics (5 events)
```

---

## 7. Type Hints Reference

### 7.1 Core Types

```python
from typing import Union, Optional, Literal
from datetime import datetime, date
from pathlib import Path

# Datetime inputs accept strings or datetime objects
DateTimeInput = Union[str, datetime]

# Path inputs accept strings or Path objects
PathInput = Union[str, Path]

# Event status values
EventStatusType = Literal["TENTATIVE", "CONFIRMED", "CANCELLED"]

# Transparency values
TransparencyType = Literal["OPAQUE", "TRANSPARENT"]

# Recurrence frequency
FrequencyType = Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]

# Days of week
DayType = Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
```

### 7.2 Full Method Signatures

```python
# CalendarBuilder
class CalendarBuilder:
    def __init__(
        self,
        calendar_name: str = "My Calendar",
        timezone: str = "UTC",
        template: str = "standard",
        validate: bool = True
    ) -> None: ...

    def add_event(
        self,
        summary: str,
        start: Union[str, datetime],
        end: Optional[Union[str, datetime]] = None,
        duration: Optional[str] = None,
        **kwargs
    ) -> 'CalendarBuilder': ...

    def add_events(self, events: list[dict]) -> 'CalendarBuilder': ...

    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> 'CalendarBuilder': ...

    @classmethod
    def from_dict(cls, data: dict) -> 'CalendarBuilder': ...

    def generate(self) -> str: ...

    def save(self, output_path: Union[str, Path]) -> Path: ...

    def save_individual_events(
        self,
        output_dir: Union[str, Path],
        filename_template: str = "event_{index}.ics"
    ) -> list[Path]: ...

    def clear_events(self) -> 'CalendarBuilder': ...

    def __len__(self) -> int: ...

    def __repr__(self) -> str: ...
```

---

## 8. Best Practices

### 8.1 For Orchestration Software

1. **Load from JSON**: Use `from_json()` for configuration-driven generation
2. **Error Handling**: Always wrap in try-except for production
3. **Validation**: Keep validation enabled unless performance-critical
4. **Timezone**: Always specify explicit timezones
5. **Batch Processing**: Generate multiple calendars in parallel if needed

```python
# Good: Configuration-driven
config = load_config("calendar_config.json")
CalendarBuilder.from_json(config["input"]).save(config["output"])

# Bad: Hardcoded values
builder = CalendarBuilder()
builder.add_event("Event", "2024-01-15T10:00:00", duration="PT1H")
```

### 8.2 Performance Optimization

1. **Disable validation** for trusted inputs:
   ```python
   builder = CalendarBuilder(validate=False)  # Skip ICS validation
   ```

2. **Reuse builder instance**:
   ```python
   builder = CalendarBuilder()
   for event_data in large_dataset:
       builder.add_event(**event_data)
   builder.save("output.ics")
   ```

3. **Batch add events**:
   ```python
   builder.add_events(event_list)  # Better than multiple add_event calls
   ```

### 8.3 Error Handling Patterns

```python
from icalendar_builder import (
    CalendarBuilder,
    ValidationError,
    TimezoneError,
    FileIOError
)

def safe_calendar_generation(input_file: str, output_file: str) -> bool:
    """Safe calendar generation with comprehensive error handling."""
    try:
        builder = CalendarBuilder.from_json(input_file)
        builder.save(output_file)
        return True

    except FileNotFoundError as e:
        logger.error(f"Input file not found: {input_file}")
        return False

    except ValidationError as e:
        logger.error(f"Invalid event data: {e}")
        if e.field:
            logger.error(f"  Problem field: {e.field}")
        return False

    except TimezoneError as e:
        logger.error(f"Invalid timezone: {e.timezone}")
        return False

    except FileIOError as e:
        logger.error(f"Cannot write to {e.path}: {e.original_error}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
```

---

## 9. API Stability Guarantees

### 9.1 Semantic Versioning

This project follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to public API
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### 9.2 Public vs Private API

**Public API** (stable, documented, versioned):
- All classes/functions exported in `__init__.py`
- All classes/functions listed in `__all__`
- All documented in this API reference

**Private API** (unstable, may change):
- Anything prefixed with `_`
- Anything in `internal/` or `_internal/` modules
- Not exported in `__init__.py`

### 9.3 Deprecation Policy

1. Deprecated features will show warnings for 2 minor versions
2. Deprecated features removed in next major version
3. Migration guide provided in CHANGELOG

Example:
```
v1.0.0: Feature X introduced
v1.5.0: Feature X deprecated (warning added)
v1.6.0: Feature X still works (warning remains)
v2.0.0: Feature X removed
```

---

## 10. Conclusion

The ICalendar Builder API is designed to be simple for common use cases while supporting advanced features when needed. Key strengths:

1. **Type-Safe**: Full type hints for IDE support and type checking
2. **Validated**: Pydantic models catch errors early
3. **Flexible**: Multiple ways to create calendars (programmatic, JSON, factories)
4. **Orchestration-Friendly**: Designed for automated workflows
5. **Well-Documented**: Comprehensive docstrings and examples

For orchestration software, the recommended pattern is:

```python
from icalendar_builder import CalendarBuilder

# Load from configuration
CalendarBuilder.from_json("config.json").save("output.ics")
```

This single line handles parsing, validation, generation, and file I/O with appropriate error handling.
