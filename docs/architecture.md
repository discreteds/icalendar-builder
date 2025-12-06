# ICalendar Builder - Architecture Design

## Document Information

**Version:** 1.0
**Date:** 2025-01-01
**Status:** Draft

## 1. Architecture Overview

### 1.1 Design Philosophy

The ICalendar Builder follows these core principles:

1. **Type Safety First**: Leverage Python's type system and Pydantic for compile-time and runtime safety
2. **Separation of Concerns**: Clear boundaries between data models, templates, generation, and validation
3. **Fail Fast**: Validate early and provide clear error messages
4. **Extensibility**: Design for extension through templates and custom properties
5. **Zero Configuration**: Sensible defaults for common use cases
6. **Testability**: Architecture that facilitates unit and integration testing

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
│                    (Orchestration Software)                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Public API                              │
│  ┌────────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ CalendarBuilder    │  │ EventFactory   │  │ Models       │  │
│  │ - add_event()      │  │ - sport_event()│  │ - Event      │  │
│  │ - from_json()      │  │ - music_event()│  │ - Collection │  │
│  │ - save()           │  │                │  │              │  │
│  └────────────────────┘  └────────────────┘  └──────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Core Components                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Validators   │  │ Templates    │  │ Generators           │  │
│  │ - Event      │  │ - Manager    │  │ - SingleEvent        │  │
│  │ - ICS        │  │ - Jinja2     │  │ - RecurringEvent     │  │
│  │              │  │ - Builtin    │  │ - Calendar           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Utility Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ DateTime     │  │ Timezone     │  │ UID Generation       │  │
│  │ Utils        │  │ Handler      │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Dependencies                         │
│     Pydantic  │  Jinja2  │  dateutil  │  zoneinfo (stdlib)     │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Component Architecture

### 2.1 Data Models Layer

#### 2.1.1 Purpose

Provide type-safe, validated data structures for all calendar entities.

#### 2.1.2 Components

**models.py**

```python
# Enum types for constrained values
class RecurrenceFrequency(str, Enum): ...
class AttendeeRole(str, Enum): ...
class AlarmAction(str, Enum): ...
class EventStatus(str, Enum): ...

# Composite models
class Organizer(BaseModel): ...
class Attendee(BaseModel): ...
class Alarm(BaseModel): ...
class Recurrence(BaseModel): ...

# Core event model
class CalendarEvent(BaseModel):
    """
    Primary event data structure.

    Responsibilities:
    - Data validation
    - Type enforcement
    - Business logic constraints (end > start)
    - Default value assignment
    """
    summary: str
    start: datetime
    end: Optional[datetime]
    duration: Optional[str]
    # ... other fields

# Collection model
class CalendarCollection(BaseModel):
    """
    Container for multiple events forming a calendar.

    Responsibilities:
    - Calendar-level metadata
    - Event aggregation
    - Timezone inheritance
    """
    calendar_name: str
    timezone: str
    events: list[CalendarEvent]
```

#### 2.1.3 Design Decisions

**Why Pydantic?**
- Runtime validation with type hints
- JSON schema generation
- Excellent IDE support
- Validation error messages
- Performance (Rust-based validation)

**Why Enums for constrained values?**
- Type safety over string literals
- Autocomplete in IDEs
- Prevents invalid values
- Clear documentation

**Model Validation Strategy:**
- Use `@field_validator` for single-field validation
- Use `@model_validator` for cross-field validation
- Fail fast with clear error messages
- Suggest corrections where possible

#### 2.1.4 Validation Rules

```python
# Field-level validation
@field_validator('timezone')
@classmethod
def validate_timezone(cls, v: str) -> str:
    """Validate IANA timezone exists."""
    try:
        ZoneInfo(v)
    except Exception:
        raise ValueError(f"Invalid timezone: {v}. Use IANA names like 'UTC', 'Europe/Paris'")
    return v

# Model-level validation
@model_validator(mode='after')
def validate_time_specification(self):
    """Ensure either end or duration is specified, not both."""
    if not self.end and not self.duration:
        raise ValueError("Must specify either 'end' or 'duration'")
    if self.end and self.duration:
        raise ValueError("Cannot specify both 'end' and 'duration'")
    return self
```

### 2.2 Template System

#### 2.2.1 Purpose

Provide flexible, extensible event rendering with separation between data and presentation.

#### 2.2.2 Architecture

```
templates/
├── __init__.py
├── base.py              # Abstract base classes
├── manager.py           # Template discovery and caching
└── builtin/
    ├── standard.ics     # General-purpose template
    ├── sport.ics        # Sports event template
    ├── music.ics        # Music/festival template
    └── recurring.ics    # Recurring event template
```

#### 2.2.3 Template Protocol

```python
class TemplateProtocol(Protocol):
    """Interface all templates must implement."""

    def render(self, event: CalendarEvent) -> str:
        """Render event to ICS VEVENT component string."""
        ...
```

#### 2.2.4 Base Template Implementation

```python
class BaseTemplate(ABC):
    """
    Abstract base class for templates.

    Responsibilities:
    - Template loading
    - Caching
    - Error handling
    """

    def __init__(self, template_path: Optional[Path] = None):
        self.template_path = template_path
        self._template_content: Optional[str] = None

    @abstractmethod
    def render(self, event: CalendarEvent) -> str:
        """Subclasses implement rendering logic."""
        pass

    def load_template(self) -> str:
        """Load template from disk (cached)."""
        if self._template_content is None and self.template_path:
            with open(self.template_path, 'r') as f:
                self._template_content = f.read()
        return self._template_content or ""
```

#### 2.2.5 Jinja2 Template Implementation

```python
class Jinja2Template(BaseTemplate):
    """
    Jinja2-based template rendering.

    Features:
    - Variable substitution
    - Conditional blocks
    - Filters for formatting
    - Template inheritance

    Security:
    - Autoescape disabled (ICS format, not HTML)
    - No arbitrary code execution
    - Sandboxed environment
    """

    def __init__(self, template_path: Path):
        super().__init__(template_path)

        # Configure Jinja2 for ICS generation
        self.env = Environment(
            loader=FileSystemLoader(template_path.parent),
            autoescape=False,        # ICS not HTML
            trim_blocks=True,        # Clean whitespace
            lstrip_blocks=True,      # Clean indentation
        )

        # Register custom filters
        self.env.filters['fold_text'] = self._fold_text
        self.env.filters['escape_text'] = self._escape_text

        self.template = self.env.get_template(template_path.name)

    def render(self, event: CalendarEvent) -> str:
        """Render event using Jinja2 template."""
        context = event.model_dump()
        return self.template.render(event=context)

    @staticmethod
    def _fold_text(text: str, width: int = 75) -> str:
        """Fold long lines per RFC 5545 (75 char limit)."""
        # Implementation details...

    @staticmethod
    def _escape_text(text: str) -> str:
        """Escape special characters for ICS format."""
        # Escape: backslash, semicolon, comma, newline
        # Implementation details...
```

#### 2.2.6 Template Manager

```python
class TemplateManager:
    """
    Central template registry and cache.

    Responsibilities:
    - Discover built-in templates
    - Load custom templates
    - Cache template instances
    - Validate template syntax
    """

    BUILTIN_TEMPLATES = {
        "standard": "builtin/standard.ics",
        "sport": "builtin/sport.ics",
        "music": "builtin/music.ics",
        "recurring": "builtin/recurring.ics",
    }

    def __init__(self):
        self.template_dir = Path(__file__).parent
        self._cache: dict[str, BaseTemplate] = {}

    def get_template(self, name: str) -> BaseTemplate:
        """
        Get template by name or path.

        Args:
            name: Built-in template name OR custom template path

        Returns:
            BaseTemplate instance

        Raises:
            FileNotFoundError: Template not found
            TemplateError: Template syntax error
        """
        if name in self._cache:
            return self._cache[name]

        # Resolve template path
        if name in self.BUILTIN_TEMPLATES:
            template_path = self.template_dir / self.BUILTIN_TEMPLATES[name]
        else:
            template_path = Path(name)
            if not template_path.exists():
                raise FileNotFoundError(
                    f"Template not found: {name}. "
                    f"Available built-in templates: {list(self.BUILTIN_TEMPLATES.keys())}"
                )

        # Create and cache template
        template = Jinja2Template(template_path)
        self._cache[name] = template
        return template

    def list_builtin_templates(self) -> list[str]:
        """Return list of available built-in templates."""
        return list(self.BUILTIN_TEMPLATES.keys())
```

#### 2.2.7 Template Design

**Standard Template (builtin/standard.ics)**

```jinja2
BEGIN:VEVENT
UID:{{ event.uid | default(generate_uid()) }}
DTSTAMP:{{ now() | datetime_format }}Z
DTSTART;TZID={{ event.timezone }}:{{ event.start | datetime_format }}
{% if event.end -%}
DTEND;TZID={{ event.timezone }}:{{ event.end | datetime_format }}
{% elif event.duration -%}
DURATION:{{ event.duration }}
{% endif -%}
SUMMARY:{{ event.summary | escape_text }}
{% if event.description -%}
DESCRIPTION:{{ event.description | escape_text | fold_text }}
{% endif -%}
{% if event.location -%}
LOCATION:{{ event.location | escape_text }}
{% endif -%}
STATUS:{{ event.status }}
TRANSP:{{ event.transparency }}
{% if event.priority > 0 -%}
PRIORITY:{{ event.priority }}
{% endif -%}
{% if event.url -%}
URL:{{ event.url }}
{% endif -%}
{% if event.organizer -%}
ORGANIZER;CN="{{ event.organizer.name | escape_text }}":mailto:{{ event.organizer.email }}
{% endif -%}
{% for attendee in event.attendees -%}
ATTENDEE;ROLE={{ attendee.role }};RSVP={{ 'TRUE' if attendee.rsvp else 'FALSE' }}{% if attendee.name %};CN="{{ attendee.name | escape_text }}"{% endif %}:mailto:{{ attendee.email }}
{% endfor -%}
{% if event.recurrence -%}
RRULE:FREQ={{ event.recurrence.frequency }}{% if event.recurrence.interval > 1 %};INTERVAL={{ event.recurrence.interval }}{% endif %}{% if event.recurrence.count %};COUNT={{ event.recurrence.count }}{% elif event.recurrence.until %};UNTIL={{ event.recurrence.until | datetime_format }}Z{% endif %}{% if event.recurrence.by_day %};BYDAY={{ event.recurrence.by_day | join(',') }}{% endif %}
{% endif -%}
{% for category in event.categories -%}
CATEGORIES:{{ category | escape_text }}
{% endfor -%}
{% for key, value in event.custom_properties.items() -%}
{{ key }}:{{ value | escape_text }}
{% endfor -%}
{% for alarm in event.alarms -%}
BEGIN:VALARM
ACTION:{{ alarm.action }}
TRIGGER:{{ alarm.trigger }}
{% if alarm.description -%}
DESCRIPTION:{{ alarm.description | escape_text }}
{% endif -%}
{% if alarm.repeat -%}
REPEAT:{{ alarm.repeat }}
DURATION:{{ alarm.duration }}
{% endif -%}
END:VALARM
{% endfor -%}
END:VEVENT
```

### 2.3 Generator Layer

#### 2.3.1 Purpose

Transform validated event models into RFC 5545-compliant ICS file content.

#### 2.3.2 Architecture

```
generators/
├── __init__.py
├── base.py           # Abstract generator interface
├── single.py         # Single event generator
├── recurring.py      # Recurring event generator
└── calendar.py       # Full calendar generator
```

#### 2.3.3 Base Generator

```python
class BaseGenerator(ABC):
    """
    Abstract base for all generators.

    Responsibilities:
    - Define generator contract
    - Common utility methods
    - Error handling patterns
    """

    @abstractmethod
    def generate(self, events: list[CalendarEvent]) -> str:
        """Generate ICS content from events."""
        pass

    def _format_datetime(self, dt: datetime, timezone: str) -> str:
        """Format datetime for ICS output."""
        # Handle timezone-aware formatting
        pass

    def _escape_text(self, text: str) -> str:
        """Escape special ICS characters."""
        return (text
            .replace('\\', '\\\\')
            .replace(';', '\\;')
            .replace(',', '\\,')
            .replace('\n', '\\n'))
```

#### 2.3.4 Calendar Generator

```python
class CalendarGenerator(BaseGenerator):
    """
    Generate complete VCALENDAR with multiple events.

    Responsibilities:
    - Generate VCALENDAR container
    - Generate VTIMEZONE components
    - Render all events
    - Assemble final ICS content
    """

    def __init__(
        self,
        calendar_name: str,
        timezone: str,
        template: BaseTemplate,
        product_id: str = "//icalendar-builder//EN"
    ):
        self.calendar_name = calendar_name
        self.timezone = timezone
        self.template = template
        self.product_id = product_id

    def generate(self, events: list[CalendarEvent]) -> str:
        """
        Generate complete ICS calendar.

        Process:
        1. Generate VCALENDAR header
        2. Collect unique timezones
        3. Generate VTIMEZONE for each timezone
        4. Render each event using template
        5. Assemble and return ICS content
        """
        parts = []

        # Header
        parts.append("BEGIN:VCALENDAR")
        parts.append("VERSION:2.0")
        parts.append(f"PRODID:{self.product_id}")
        parts.append(f"X-WR-CALNAME:{self._escape_text(self.calendar_name)}")
        parts.append(f"X-WR-TIMEZONE:{self.timezone}")

        # Collect unique timezones
        timezones = self._collect_timezones(events)

        # Generate VTIMEZONE components
        for tz_name in timezones:
            vtimezone = self._generate_vtimezone(tz_name)
            parts.append(vtimezone)

        # Render each event
        for event in events:
            vevent = self.template.render(event)
            parts.append(vevent)

        # Footer
        parts.append("END:VCALENDAR")

        return "\n".join(parts)

    def _collect_timezones(self, events: list[CalendarEvent]) -> set[str]:
        """Collect unique timezone identifiers from events."""
        timezones = {self.timezone}  # Include calendar default
        for event in events:
            if event.timezone:
                timezones.add(event.timezone)
        return timezones

    def _generate_vtimezone(self, timezone_name: str) -> str:
        """
        Generate VTIMEZONE component.

        Uses zoneinfo + dateutil to generate proper
        STANDARD and DAYLIGHT components with correct
        offsets and transitions.
        """
        from utils.timezone import TimezoneHandler
        return TimezoneHandler.generate_vtimezone(timezone_name)
```

### 2.4 Validation Layer

#### 2.4.1 Purpose

Ensure data integrity at multiple levels: input validation, semantic validation, and output validation.

#### 2.4.2 Validation Strategy

```
┌──────────────────────┐
│   Input Data         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Pydantic Validation  │  ← Type checking, required fields
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Semantic Validation  │  ← Business rules (end > start)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Event Generation     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ ICS Validation       │  ← RFC 5545 compliance
└──────────────────────┘
```

#### 2.4.3 Event Validator

```python
class EventValidator:
    """
    Semantic validation beyond Pydantic schema.

    Validates:
    - Datetime ranges (end > start)
    - Recurrence rule consistency
    - Alarm trigger validity
    - Email format for organizer/attendees
    """

    def validate_event(self, event: CalendarEvent) -> None:
        """
        Perform comprehensive event validation.

        Raises:
            ValidationError: If event is invalid
        """
        self._validate_datetime_range(event)
        self._validate_recurrence(event)
        self._validate_alarms(event)
        self._validate_attendees(event)

    def _validate_datetime_range(self, event: CalendarEvent) -> None:
        """Ensure end datetime is after start."""
        if event.end and event.end <= event.start:
            raise ValidationError(
                f"Event end ({event.end}) must be after start ({event.start})"
            )

    def _validate_recurrence(self, event: CalendarEvent) -> None:
        """Validate recurrence rule if present."""
        if not event.recurrence:
            return

        # Check mutually exclusive end conditions
        if event.recurrence.count and event.recurrence.until:
            raise ValidationError(
                "Recurrence cannot specify both 'count' and 'until'"
            )

        # Validate by_day values
        if event.recurrence.by_day:
            valid_days = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}
            invalid = set(event.recurrence.by_day) - valid_days
            if invalid:
                raise ValidationError(
                    f"Invalid recurrence days: {invalid}. "
                    f"Valid values: {valid_days}"
                )
```

#### 2.4.4 ICS Validator

```python
class ICSValidator:
    """
    Validate generated ICS content for RFC 5545 compliance.

    Validation levels:
    1. Structural: BEGIN/END pairs, required components
    2. Syntactic: Line folding, character encoding
    3. Semantic: Valid property values

    Uses icalendar library for parsing validation.
    """

    def validate(self, ics_content: str) -> bool:
        """
        Validate ICS content.

        Args:
            ics_content: ICS file content as string

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid with details
        """
        # Structural validation
        self._validate_structure(ics_content)

        # Parse with icalendar library
        try:
            from icalendar import Calendar
            Calendar.from_ical(ics_content)
        except Exception as e:
            raise ValidationError(f"ICS parsing failed: {e}")

        # Additional custom validation
        self._validate_line_length(ics_content)
        self._validate_required_properties(ics_content)

        return True

    def _validate_structure(self, content: str) -> None:
        """Validate basic ICS structure."""
        if not content.startswith("BEGIN:VCALENDAR"):
            raise ValidationError("ICS must start with BEGIN:VCALENDAR")

        if not content.strip().endswith("END:VCALENDAR"):
            raise ValidationError("ICS must end with END:VCALENDAR")

        # Count BEGIN/END pairs
        begin_count = content.count("BEGIN:VEVENT")
        end_count = content.count("END:VEVENT")
        if begin_count != end_count:
            raise ValidationError(
                f"Mismatched VEVENT blocks: {begin_count} BEGIN, {end_count} END"
            )

    def _validate_line_length(self, content: str) -> None:
        """Validate RFC 5545 line length (75 chars)."""
        for i, line in enumerate(content.split('\n'), 1):
            if line.startswith(' '):  # Folded line continuation
                continue
            if len(line) > 75:
                raise ValidationError(
                    f"Line {i} exceeds 75 characters (RFC 5545). "
                    f"Use line folding for long content."
                )
```

### 2.5 Utility Layer

#### 2.5.1 DateTime Utilities

```python
class DateTimeUtils:
    """
    DateTime handling utilities.

    Functions:
    - Parse various datetime formats
    - Format for ICS output
    - Duration calculation
    - ISO 8601 duration parsing
    """

    @staticmethod
    def parse_datetime(dt_str: str, timezone: Optional[str] = None) -> datetime:
        """
        Parse datetime string to datetime object.

        Supports:
        - ISO 8601: 2024-06-29T09:00:00
        - ICS format: 20240629T090000
        - Date only: 2024-06-29 (assumes midnight)
        """
        from dateutil.parser import parse

        dt = parse(dt_str)

        if timezone and dt.tzinfo is None:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(timezone))

        return dt

    @staticmethod
    def format_ics_datetime(dt: datetime, timezone: str) -> str:
        """Format datetime for ICS output (YYYYMMDDTHHmmss)."""
        # Apply timezone if needed
        if dt.tzinfo is None:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(timezone))

        return dt.strftime('%Y%m%dT%H%M%S')

    @staticmethod
    def calculate_duration(start: datetime, end: datetime) -> str:
        """
        Calculate ISO 8601 duration between datetimes.

        Returns: PTxHxMxS format
        Example: PT2H30M0S (2 hours 30 minutes)
        """
        delta = end - start
        total_seconds = int(delta.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"PT{hours}H{minutes}M{seconds}S"

    @staticmethod
    def parse_duration(duration_str: str) -> timedelta:
        """Parse ISO 8601 duration to timedelta."""
        import re

        pattern = r'P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?'
        match = re.match(pattern, duration_str)

        if not match:
            raise ValueError(f"Invalid ISO 8601 duration: {duration_str}")

        # Extract components and convert to timedelta
        # (simplified - full implementation would handle years/months)
        ...
```

#### 2.5.2 Timezone Handler

```python
class TimezoneHandler:
    """
    Timezone management and VTIMEZONE generation.

    Responsibilities:
    - Validate IANA timezone names
    - Generate VTIMEZONE components
    - Handle DST transitions
    - Localize naive datetimes
    """

    @staticmethod
    def validate_timezone(timezone_name: str) -> bool:
        """Check if timezone name is valid IANA identifier."""
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(timezone_name)
            return True
        except Exception:
            return False

    @staticmethod
    def generate_vtimezone(timezone_name: str) -> str:
        """
        Generate VTIMEZONE component for timezone.

        Strategy:
        1. Use icalendar library's Timezone class
        2. Generate STANDARD and DAYLIGHT components
        3. Calculate offsets from UTC
        4. Determine DST transition rules

        Returns: VTIMEZONE component as string
        """
        from icalendar import Timezone, TimezoneDaylight, TimezoneStandard
        from zoneinfo import ZoneInfo
        from datetime import datetime

        tz = ZoneInfo(timezone_name)
        vtimezone = Timezone()
        vtimezone.add('tzid', timezone_name)

        # Determine if timezone has DST
        # Find transitions and generate STANDARD/DAYLIGHT
        # (Implementation details depend on zoneinfo API)

        return vtimezone.to_ical().decode('utf-8')

    @staticmethod
    def localize_datetime(dt: datetime, timezone_name: str) -> datetime:
        """Attach timezone info to naive datetime."""
        if dt.tzinfo is not None:
            return dt

        from zoneinfo import ZoneInfo
        return dt.replace(tzinfo=ZoneInfo(timezone_name))
```

#### 2.5.3 UID Generator

```python
class UIDGenerator:
    """
    Generate unique identifiers for events.

    Format: {uuid}@{domain}
    Example: 550e8400-e29b-41d4-a716-446655440000@icalendar-builder.local
    """

    def __init__(self, domain: str = "icalendar-builder.local"):
        self.domain = domain

    def generate(self, event_hint: Optional[str] = None) -> str:
        """
        Generate unique event UID.

        Args:
            event_hint: Optional hint for UID (event summary)

        Returns:
            Unique identifier string
        """
        import uuid
        uid = str(uuid.uuid4())
        return f"{uid}@{self.domain}"

    @staticmethod
    def validate_uid(uid: str) -> bool:
        """Validate UID format."""
        # UIDs should not contain whitespace or certain special chars
        if ' ' in uid or '\n' in uid or '\t' in uid:
            return False
        return True
```

### 2.6 Exception Hierarchy

```python
class ICSBuilderError(Exception):
    """Base exception for all icalendar-builder errors."""
    pass

class ValidationError(ICSBuilderError):
    """Data validation failed."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message)

class TemplateError(ICSBuilderError):
    """Template rendering failed."""
    pass

class TimezoneError(ICSBuilderError):
    """Invalid or unsupported timezone."""

    def __init__(self, timezone: str, message: Optional[str] = None):
        self.timezone = timezone
        msg = message or f"Invalid timezone: {timezone}"
        super().__init__(msg)

class GenerationError(ICSBuilderError):
    """ICS generation failed."""
    pass

class IOError(ICSBuilderError):
    """File I/O operation failed."""

    def __init__(self, path: Path, operation: str, original_error: Exception):
        self.path = path
        self.operation = operation
        self.original_error = original_error
        super().__init__(
            f"Failed to {operation} file {path}: {original_error}"
        )
```

## 3. Data Flow Architecture

### 3.1 Standard Usage Flow

```
┌──────────────────────┐
│  JSON Input File     │
│  or Dictionary       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  CalendarBuilder.from_json() / from_dict()           │
│  - Load JSON                                         │
│  - Parse to CalendarCollection model                 │
│  - Validate with Pydantic                            │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  CalendarEvent Models (validated)                    │
│  - Type-checked                                      │
│  - Business rules validated                          │
│  - UID assigned if missing                           │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  CalendarGenerator.generate()                        │
│  - Select template                                   │
│  - Collect unique timezones                          │
│  - Generate VTIMEZONE components                     │
│  - Render each event                                 │
│  - Assemble ICS content                              │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  ICS Content (string)                                │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  ICSValidator.validate() (if enabled)                │
│  - Structural validation                             │
│  - RFC 5545 compliance                               │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  File I/O                                            │
│  - Write to .ics file                                │
│  - Return Path object                                │
└──────────────────────────────────────────────────────┘
```

### 3.2 Programmatic API Flow

```python
# Flow 1: Simple programmatic usage
builder = CalendarBuilder(timezone="Europe/Paris")
builder.add_event(
    summary="Event 1",
    start="2024-06-29T09:00:00",
    end="2024-06-29T17:00:00"
)
builder.save("output.ics")

# Flow 2: Method chaining
(CalendarBuilder(timezone="UTC")
    .add_event(summary="Event 1", start=..., end=...)
    .add_event(summary="Event 2", start=..., end=...)
    .save("output.ics"))

# Flow 3: JSON-based (orchestration)
CalendarBuilder.from_json("events.json").save("output.ics")

# Flow 4: Factory pattern
from icalendar_builder import EventFactory

event = EventFactory.sport_event(
    sport_name="Cycling",
    event_name="Tour de France Stage 1",
    start=datetime(2024, 6, 29, 9, 0),
    duration="PT8H"
)
builder.add_event(**event.model_dump())
```

## 4. Design Patterns

### 4.1 Builder Pattern

**CalendarBuilder** uses the builder pattern for fluent API:

```python
builder = (CalendarBuilder()
    .add_event(...)
    .add_event(...)
    .save("output.ics"))
```

Benefits:
- Readable code
- Step-by-step construction
- Immutable until save()

### 4.2 Factory Pattern

**EventFactory** provides factory methods for common event types:

```python
sport_event = EventFactory.sport_event(...)
music_event = EventFactory.music_event(...)
meeting = EventFactory.recurring_meeting(...)
```

Benefits:
- Encapsulate event creation logic
- Type-specific defaults
- Reduce boilerplate

### 4.3 Strategy Pattern

**Templates** use strategy pattern for rendering:

```python
template: BaseTemplate = TemplateManager().get_template("standard")
ics_content = template.render(event)
```

Benefits:
- Swap rendering strategies
- Extend with new templates
- Test templates independently

### 4.4 Template Method Pattern

**BaseGenerator** defines generation algorithm with hooks:

```python
class BaseGenerator(ABC):
    def generate(self, events):
        self._validate_events(events)
        self._prepare_context()
        return self._render()

    @abstractmethod
    def _render(self):
        pass
```

Benefits:
- Consistent generation flow
- Extensible steps
- Enforce contracts

## 5. Performance Considerations

### 5.1 Template Caching

Templates are loaded once and cached:

```python
class TemplateManager:
    def __init__(self):
        self._cache: dict[str, BaseTemplate] = {}

    def get_template(self, name: str) -> BaseTemplate:
        if name in self._cache:
            return self._cache[name]  # O(1) lookup
        # ... load and cache
```

### 5.2 Lazy Evaluation

- Models don't generate ICS until requested
- Validation skippable for performance
- UID generation deferred until needed

### 5.3 Batch Processing

For large event sets:

```python
# Process in chunks if needed
for chunk in chunks(events, size=1000):
    builder.add_events(chunk)
```

### 5.4 Memory Efficiency

- Streaming file writes for large calendars
- No intermediate copies of data
- Generator expressions where appropriate

## 6. Testing Architecture

### 6.1 Test Structure

```
tests/
├── unit/               # Fast, isolated tests
│   ├── test_models.py       # Pydantic validation
│   ├── test_templates.py    # Template rendering
│   ├── test_generators.py   # Generation logic
│   └── test_validators.py   # Validation logic
├── integration/        # End-to-end tests
│   ├── test_calendar_generation.py
│   └── test_file_io.py
└── fixtures/           # Test data
    ├── events/
    └── templates/
```

### 6.2 Test Strategy

```python
# Unit test example
def test_event_validation_requires_summary():
    with pytest.raises(ValidationError):
        CalendarEvent(
            summary="",  # Invalid
            start="2024-01-15T10:00:00"
        )

# Integration test example
def test_generate_complete_calendar(tmp_path):
    builder = CalendarBuilder.from_json("test_events.json")
    output = tmp_path / "calendar.ics"
    builder.save(output)

    # Verify file exists and is valid
    assert output.exists()
    content = output.read_text()
    assert content.startswith("BEGIN:VCALENDAR")

    # Parse with external library
    from icalendar import Calendar
    cal = Calendar.from_ical(content)
    assert len(cal.subcomponents) > 0
```

### 6.3 Test Coverage Goals

- Unit tests: 90%+ coverage
- All public APIs tested
- Error paths tested
- Edge cases (timezone boundaries, DST transitions)

## 7. Security Considerations

### 7.1 Template Security

- Jinja2 with autoescape disabled (ICS not HTML)
- No arbitrary code execution
- User input sanitized/escaped
- Template sandbox environment

### 7.2 File I/O Security

- Validate output paths (prevent directory traversal)
- Check file permissions before writing
- No execution of file contents
- Atomic file writes

### 7.3 Input Validation

- Validate all user input via Pydantic
- Sanitize strings for ICS format
- Prevent injection attacks
- Limit input sizes (e.g., max event count)

## 8. Extensibility Points

### 8.1 Custom Templates

Users can provide custom Jinja2 templates:

```python
builder = CalendarBuilder(template="/path/to/custom.ics")
```

### 8.2 Custom Validators

Extend validation:

```python
class CustomEventValidator(EventValidator):
    def validate_event(self, event):
        super().validate_event(event)
        # Additional validation
```

### 8.3 Custom Generators

Implement custom generation logic:

```python
class CustomGenerator(BaseGenerator):
    def generate(self, events):
        # Custom ICS generation
        pass
```

### 8.4 Pluggable Components

Future: Plugin system for:
- Custom event types
- Custom properties
- Import formats
- Export formats

## 9. Migration from Legacy Code

### 9.1 Compatibility Layer

Provide migration utilities:

```python
from icalendar_builder.legacy import convert_legacy_format

old_events = [...]  # Legacy format
new_data = convert_legacy_format(old_events, timezone="UTC")
builder = CalendarBuilder.from_dict(new_data)
```

### 9.2 Incremental Migration

Support mixed usage:
1. Use new library alongside old code
2. Migrate one notebook at a time
3. Validate outputs match
4. Remove old code once verified

## 10. Future Enhancements

### 10.1 Planned Features

- Import/parse existing ICS files
- Calendar diff and merge
- Async I/O support
- Performance optimizations for very large calendars

### 10.2 Architecture for Future Features

Design is extensible for:
- Additional output formats (JSON, XML)
- Cloud storage integration
- API integration (Google Calendar, etc.)
- Web UI (separate package)

## Appendix A: Component Dependency Graph

```
┌────────────────────────────────────────────────────────┐
│                    Application Layer                    │
│                  (CalendarBuilder API)                  │
└─────────┬──────────────────────────────────────────────┘
          │
          ├─────────────┬──────────────┬──────────────────┐
          ▼             ▼              ▼                  ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌────────────┐
    │ Models  │   │Templates │   │Generators│   │ Validators │
    └────┬────┘   └────┬─────┘   └────┬─────┘   └─────┬──────┘
         │             │              │               │
         └─────────────┴──────────────┴───────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Utils Layer   │
              │  - DateTime    │
              │  - Timezone    │
              │  - UID         │
              └────────┬───────┘
                       │
                       ▼
              ┌────────────────┐
              │  Dependencies  │
              │  - Pydantic    │
              │  - Jinja2      │
              │  - dateutil    │
              └────────────────┘
```

## Appendix B: Class Diagram

```
┌─────────────────────────┐
│  CalendarBuilder        │
├─────────────────────────┤
│ - calendar_name: str    │
│ - timezone: str         │
│ - events: list[Event]   │
│ - template: str         │
├─────────────────────────┤
│ + add_event()           │
│ + from_json()           │
│ + save()                │
│ + generate()            │
└───────────┬─────────────┘
            │ uses
            ▼
┌─────────────────────────┐
│  CalendarEvent          │
├─────────────────────────┤
│ - summary: str          │
│ - start: datetime       │
│ - end: datetime?        │
│ - duration: str?        │
│ - timezone: str         │
├─────────────────────────┤
│ + validate()            │
│ + model_dump()          │
└─────────────────────────┘

┌─────────────────────────┐
│  TemplateManager        │
├─────────────────────────┤
│ - _cache: dict          │
├─────────────────────────┤
│ + get_template()        │
│ + list_builtin()        │
└───────────┬─────────────┘
            │ manages
            ▼
┌─────────────────────────┐
│  <<interface>>          │
│  BaseTemplate           │
├─────────────────────────┤
│ + render(event)         │
└───────────▲─────────────┘
            │ implements
            │
┌───────────┴─────────────┐
│  Jinja2Template         │
├─────────────────────────┤
│ - env: Environment      │
│ - template: Template    │
├─────────────────────────┤
│ + render(event)         │
└─────────────────────────┘
```

## Conclusion

This architecture provides a solid foundation for a production-ready ICS calendar generation library. Key strengths:

1. **Type Safety**: Pydantic models with validation
2. **Separation of Concerns**: Clear component boundaries
3. **Extensibility**: Template system, custom validators
4. **Testability**: Modular design, dependency injection
5. **Performance**: Caching, lazy evaluation, batch processing
6. **Maintainability**: Clear patterns, comprehensive documentation

The architecture supports the primary use case (orchestration software) while remaining flexible for future enhancements.
