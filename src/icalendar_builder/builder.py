"""Main CalendarBuilder API and EventFactory."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict

from .models import CalendarEvent, CalendarCollection, Alarm, AlarmAction
from .templates.manager import TemplateManager
from .generators.calendar import CalendarGenerator
from .exceptions import ValidationError, FileIOError


# Default reminder settings per template type (in minutes)
TEMPLATE_REMINDER_DEFAULTS: Dict[str, int] = {
    "music": 15,
    "sport": 30,
    "standard": 60,
    "recurring": 60,
}


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
        validate: bool = True,
        default_reminder: Optional[bool] = None,
        reminder_minutes: Optional[int] = None,
    ) -> None:
        """
        Initialize calendar builder.

        Args:
            calendar_name: Name of the calendar (appears in calendar apps)
            timezone: Default IANA timezone for all events
            template: Template name ("standard", "sport", "music", "recurring")
                     or path to custom template file
            validate: Whether to validate generated ICS for RFC 5545 compliance
            default_reminder: Whether to add reminders to events without alarms.
                            None (default) = True, uses template-based defaults.
                            True = enabled with template defaults.
                            False = disabled.
            reminder_minutes: Minutes before event for reminder. None = use template
                            default (music: 15, sport: 30, standard/recurring: 60)

        Raises:
            TimezoneError: If timezone is not a valid IANA identifier
        """
        self.calendar_name = calendar_name
        self.timezone = timezone
        self.events: List[CalendarEvent] = []
        self.template_manager = TemplateManager()
        self.template = template
        self.validate = validate

        # Reminder configuration
        # default_reminder: None means True (enabled by default)
        self.default_reminder = default_reminder if default_reminder is not None else True
        # reminder_minutes: None means use template default
        self.reminder_minutes = reminder_minutes

    def add_event(
        self,
        summary: str,
        start: Union[str, datetime],
        end: Optional[Union[str, datetime]] = None,
        duration: Optional[str] = None,
        **kwargs,
    ) -> "CalendarBuilder":
        """
        Add an event to the calendar.

        Args:
            summary: Event title (required)
            start: Start datetime as ISO 8601 string or datetime object (required)
            end: End datetime (required if duration not provided)
            duration: ISO 8601 duration string (required if end not provided)
            **kwargs: Additional event properties (description, location, etc.)

        Returns:
            Self for method chaining

        Raises:
            ValidationError: If event data is invalid
        """
        # Parse datetime strings
        from .utils.datetime import DateTimeUtils

        if isinstance(start, str):
            start = DateTimeUtils.parse_datetime(start)
        if isinstance(end, str):
            end = DateTimeUtils.parse_datetime(end)

        # Build event data
        event_data = {
            "summary": summary,
            "start": start,
            "end": end,
            "duration": duration,
            "timezone": kwargs.pop("timezone", self.timezone),
            **kwargs,
        }

        # Inject default alarm if reminders enabled and no alarms provided
        if self.default_reminder and "alarms" not in event_data:
            event_data["alarms"] = [self._create_default_alarm(summary)]

        try:
            event = CalendarEvent(**event_data)
            self.events.append(event)
        except Exception as e:
            raise ValidationError(f"Invalid event data: {e}")

        return self

    def _create_default_alarm(self, event_summary: str) -> Alarm:
        """
        Create a default alarm based on template settings.

        Args:
            event_summary: Event title to include in alarm description

        Returns:
            Alarm object configured with appropriate trigger time
        """
        # Use explicit reminder_minutes or fall back to template default
        if self.reminder_minutes is not None:
            minutes = self.reminder_minutes
        else:
            minutes = TEMPLATE_REMINDER_DEFAULTS.get(self.template, 60)

        return Alarm(
            action=AlarmAction.DISPLAY,
            trigger=f"-PT{minutes}M",
            description=f"{event_summary} starts in {minutes} minutes",
        )

    def add_events(self, events: List[dict]) -> "CalendarBuilder":
        """
        Add multiple events from a list of dictionaries.

        Args:
            events: List of event dictionaries with same structure as add_event kwargs

        Returns:
            Self for method chaining

        Raises:
            ValidationError: If any event data is invalid
        """
        for event_data in events:
            if "timezone" not in event_data:
                event_data["timezone"] = self.timezone

            # Inject default alarm if reminders enabled and no alarms provided
            if self.default_reminder and "alarms" not in event_data:
                summary = event_data.get("summary", "Event")
                event_data["alarms"] = [self._create_default_alarm(summary)]

            try:
                event = CalendarEvent(**event_data)
                self.events.append(event)
            except Exception as e:
                raise ValidationError(f"Invalid event data: {e}")

        return self

    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> "CalendarBuilder":
        """
        Create builder from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            CalendarBuilder instance with events loaded

        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValidationError: If JSON structure is invalid
        """
        json_path = Path(json_path)

        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        try:
            with open(json_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            raise FileIOError(json_path, "read", e)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "CalendarBuilder":
        """
        Create builder from dictionary.

        Args:
            data: Dictionary with CalendarCollection structure

        Returns:
            CalendarBuilder instance with events loaded

        Raises:
            ValidationError: If data structure is invalid
        """
        try:
            collection = CalendarCollection(**data)
        except Exception as e:
            raise ValidationError(f"Invalid calendar data: {e}")

        builder = cls(
            calendar_name=collection.calendar_name,
            timezone=collection.timezone,
        )
        builder.events = collection.events
        return builder

    def generate(self) -> str:
        """
        Generate ICS calendar content as string.

        Returns:
            ICS file content as string

        Raises:
            ValidationError: If validation enabled and ICS is invalid
            TemplateError: If template rendering fails
            GenerationError: If ICS generation fails
        """
        if not self.events:
            raise ValidationError("Cannot generate calendar with no events")

        # Get template
        template = self.template_manager.get_template(self.template)

        # Generate calendar
        generator = CalendarGenerator(
            calendar_name=self.calendar_name,
            timezone=self.timezone,
            template=template,
        )

        ics_content = generator.generate(self.events)

        # Optional validation
        if self.validate:
            self._validate_ics(ics_content)

        return ics_content

    def save(self, output_path: Union[str, Path]) -> Path:
        """
        Save calendar to ICS file.

        Creates parent directories if they don't exist.

        Args:
            output_path: Output file path (with .ics extension)

        Returns:
            Path object pointing to saved file

        Raises:
            ValidationError: If validation enabled and ICS is invalid
            FileIOError: If file cannot be written
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate()

        try:
            output_path.write_text(content)
        except Exception as e:
            raise FileIOError(output_path, "write", e)

        return output_path

    def save_individual_events(
        self,
        output_dir: Union[str, Path],
        filename_template: str = "event_{index}.ics",
    ) -> List[Path]:
        """
        Save each event as a separate ICS file.

        Args:
            output_dir: Directory for output files
            filename_template: Template for filenames with {index} placeholder

        Returns:
            List of Path objects for all created files

        Raises:
            FileIOError: If files cannot be written
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        template = self.template_manager.get_template(self.template)

        for i, event in enumerate(self.events, start=1):
            # Generate filename
            filename = filename_template.format(
                index=i,
                summary=self._sanitize_filename(event.summary),
            )
            filepath = output_dir / filename

            # Generate single-event calendar
            generator = CalendarGenerator(
                calendar_name=self.calendar_name,
                timezone=self.timezone,
                template=template,
            )
            content = generator.generate([event])

            # Write file
            try:
                filepath.write_text(content)
                saved_files.append(filepath)
            except Exception as e:
                raise FileIOError(filepath, "write", e)

        return saved_files

    def clear_events(self) -> "CalendarBuilder":
        """
        Remove all events from the builder.

        Returns:
            Self for method chaining
        """
        self.events.clear()
        return self

    def __len__(self) -> int:
        """Return number of events in the builder."""
        return len(self.events)

    def __repr__(self) -> str:
        """String representation of builder."""
        return f"CalendarBuilder(name='{self.calendar_name}', events={len(self.events)})"

    def _validate_ics(self, ics_content: str) -> None:
        """
        Validate ICS content (basic validation).

        Args:
            ics_content: ICS file content

        Raises:
            ValidationError: If ICS is invalid
        """
        # Basic structural validation
        if not ics_content.startswith("BEGIN:VCALENDAR"):
            raise ValidationError("ICS must start with BEGIN:VCALENDAR")

        if not ics_content.strip().endswith("END:VCALENDAR"):
            raise ValidationError("ICS must end with END:VCALENDAR")

        # Count BEGIN/END pairs
        begin_count = ics_content.count("BEGIN:VEVENT")
        end_count = ics_content.count("END:VEVENT")
        if begin_count != end_count:
            raise ValidationError(
                f"Mismatched VEVENT blocks: {begin_count} BEGIN, {end_count} END"
            )

    @staticmethod
    def _sanitize_filename(text: str) -> str:
        """
        Sanitize text for use in filename.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text safe for filenames
        """
        # Replace unsafe characters
        safe = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in text)
        # Replace spaces with underscores
        safe = safe.replace(" ", "_")
        # Limit length
        return safe[:50]


class EventFactory:
    """
    Factory for creating common event types with sensible defaults.
    """

    @staticmethod
    def sport_event(
        sport_name: str,
        event_name: str,
        start: datetime,
        duration: str = "PT2H",
        location: Optional[str] = None,
        **kwargs,
    ) -> CalendarEvent:
        """
        Create a sports event with appropriate defaults.

        Args:
            sport_name: Name of the sport (e.g., "Cycling", "Football")
            event_name: Specific event description
            start: Event start datetime
            duration: ISO 8601 duration (default: 2 hours)
            location: Event location
            **kwargs: Additional event properties

        Returns:
            CalendarEvent model
        """
        return CalendarEvent(
            summary=f"{sport_name} - {event_name}",
            start=start,
            duration=duration,
            location=location,
            categories=["Sports", sport_name],
            custom_properties={"X-SPORT-TYPE": sport_name},
            **kwargs,
        )

    @staticmethod
    def music_event(
        artist: str,
        venue: str,
        start: datetime,
        end: datetime,
        ticket_url: Optional[str] = None,
        **kwargs,
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
        """
        from .models import Alarm, AlarmAction

        return CalendarEvent(
            summary=artist,
            location=venue,
            start=start,
            end=end,
            categories=["Music", "Concert"],
            alarms=[Alarm(action=AlarmAction.DISPLAY, trigger="-PT15M")],
            url=ticket_url,
            **kwargs,
        )

    @staticmethod
    def recurring_meeting(
        summary: str,
        start: datetime,
        duration: str,
        frequency: str,
        count: Optional[int] = None,
        until: Optional[datetime] = None,
        by_day: Optional[List[str]] = None,
        **kwargs,
    ) -> CalendarEvent:
        """
        Create a recurring meeting event.

        Args:
            summary: Meeting title
            start: First occurrence start datetime
            duration: Meeting duration (ISO 8601)
            frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY, YEARLY)
            count: Number of occurrences
            until: Recurrence end date
            by_day: Days of week (e.g., ["MO", "WE", "FR"])
            **kwargs: Additional event properties

        Returns:
            CalendarEvent model
        """
        from .models import Recurrence, RecurrenceFrequency

        return CalendarEvent(
            summary=summary,
            start=start,
            duration=duration,
            recurrence=Recurrence(
                frequency=RecurrenceFrequency(frequency),
                count=count,
                until=until,
                by_day=by_day,
            ),
            categories=["Meeting"],
            **kwargs,
        )

    @staticmethod
    def all_day_event(
        summary: str,
        date: Union[str, datetime],
        location: Optional[str] = None,
        **kwargs,
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
        """
        from .utils.datetime import DateTimeUtils

        if isinstance(date, str):
            start = DateTimeUtils.parse_datetime(date)
        else:
            start = datetime.combine(date, datetime.min.time())

        return CalendarEvent(
            summary=summary,
            start=start,
            duration="P1D",  # 24 hours
            location=location,
            transparency="TRANSPARENT",  # Doesn't block time
            **kwargs,
        )
