"""ICalendar Builder - Modern Python library for generating ICS calendar files."""

from .__version__ import __version__
from .builder import CalendarBuilder, EventFactory, TEMPLATE_REMINDER_DEFAULTS
from .exceptions import (
    FileIOError,
    GenerationError,
    ICSBuilderError,
    TemplateError,
    TimezoneError,
    ValidationError,
)
from .models import (
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

__all__ = [
    "__version__",
    # Main API
    "CalendarBuilder",
    "EventFactory",
    "TEMPLATE_REMINDER_DEFAULTS",
    # Exceptions
    "ICSBuilderError",
    "ValidationError",
    "TemplateError",
    "TimezoneError",
    "GenerationError",
    "FileIOError",
    # Models
    "CalendarEvent",
    "CalendarCollection",
    "Organizer",
    "Attendee",
    "Alarm",
    "Recurrence",
    # Enums
    "RecurrenceFrequency",
    "AttendeeRole",
    "AlarmAction",
    "EventStatus",
]
