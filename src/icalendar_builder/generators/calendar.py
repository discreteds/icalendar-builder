"""Calendar generator for complete ICS file generation."""

from typing import List, Set

from .base import BaseGenerator
from ..models import CalendarEvent
from ..templates.base import BaseTemplate
from ..utils.timezone import TimezoneHandler
from ..utils.uid import UIDGenerator


class CalendarGenerator(BaseGenerator):
    """
    Generate complete VCALENDAR with multiple events.

    This is the main generator that produces RFC 5545-compliant ICS files.
    """

    def __init__(
        self,
        calendar_name: str,
        timezone: str,
        template: BaseTemplate,
        product_id: str = "//icalendar-builder//EN",
    ) -> None:
        """
        Initialize calendar generator.

        Args:
            calendar_name: Name of the calendar
            timezone: Default timezone
            template: Template for rendering events
            product_id: PRODID for the calendar
        """
        self.calendar_name = calendar_name
        self.timezone = timezone
        self.template = template
        self.product_id = product_id
        self.uid_generator = UIDGenerator()

    def generate(self, events: List[CalendarEvent]) -> str:
        """
        Generate complete ICS calendar.

        Process:
        1. Generate VCALENDAR header
        2. Collect unique timezones
        3. Generate VTIMEZONE for each timezone
        4. Render each event using template
        5. Assemble and return ICS content

        Args:
            events: List of calendar events

        Returns:
            Complete ICS file content
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
        for tz_name in sorted(timezones):  # Sort for consistent output
            vtimezone = TimezoneHandler.generate_vtimezone(tz_name)
            parts.append(vtimezone)

        # Ensure events have UIDs
        for event in events:
            if not event.uid:
                event.uid = self.uid_generator.generate()

        # Render each event
        for event in events:
            vevent = self.template.render(event)
            parts.append(vevent)

        # Footer
        parts.append("END:VCALENDAR")

        return "\r\n".join(parts)

    def _collect_timezones(self, events: List[CalendarEvent]) -> Set[str]:
        """
        Collect unique timezone identifiers from events.

        Args:
            events: List of calendar events

        Returns:
            Set of unique timezone names
        """
        timezones = {self.timezone}  # Include calendar default
        for event in events:
            if event.timezone:
                timezones.add(event.timezone)
        return timezones
