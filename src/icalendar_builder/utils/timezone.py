"""Timezone management and VTIMEZONE generation."""

from datetime import datetime
from typing import Set
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneHandler:
    """Timezone management and VTIMEZONE generation."""

    @staticmethod
    def validate_timezone(timezone_name: str) -> bool:
        """
        Check if timezone name is valid IANA identifier.

        Args:
            timezone_name: IANA timezone name

        Returns:
            True if valid, False otherwise

        Example:
            >>> TimezoneHandler.validate_timezone("Europe/Paris")
            True
            >>> TimezoneHandler.validate_timezone("Invalid/Timezone")
            False
        """
        try:
            ZoneInfo(timezone_name)
            return True
        except ZoneInfoNotFoundError:
            return False

    @staticmethod
    def generate_vtimezone(timezone_name: str) -> str:
        """
        Generate VTIMEZONE component for timezone.

        This creates a simplified VTIMEZONE component that works with most
        calendar applications. For production use, consider using a more
        comprehensive timezone database.

        Args:
            timezone_name: IANA timezone name

        Returns:
            VTIMEZONE component as string

        Example:
            >>> tz = TimezoneHandler.generate_vtimezone("UTC")
            >>> "BEGIN:VTIMEZONE" in tz
            True
        """
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            # Fallback to simple UTC timezone
            return "BEGIN:VTIMEZONE\r\nTZID:{}\r\nBEGIN:STANDARD\r\nDTSTART:19700101T000000\r\nTZOFFSETFROM:+0000\r\nTZOFFSETTO:+0000\r\nTZNAME:UTC\r\nEND:STANDARD\r\nEND:VTIMEZONE".format(timezone_name)

        # For common timezones, use simplified definitions
        # This is a basic implementation; production should use full tzdata

        # Get a sample datetime to determine offset
        sample_dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=tz)
        offset = sample_dt.strftime("%z")
        offset_formatted = f"{offset[:3]}:{offset[3:]}" if offset else "+00:00"

        # Simple VTIMEZONE (works for most cases)
        return "BEGIN:VTIMEZONE\r\nTZID:{}\r\nBEGIN:STANDARD\r\nDTSTART:19700101T000000\r\nTZOFFSETFROM:{}\r\nTZOFFSETTO:{}\r\nTZNAME:{}\r\nEND:STANDARD\r\nEND:VTIMEZONE".format(
            timezone_name,
            offset_formatted.replace(':', ''),
            offset_formatted.replace(':', ''),
            timezone_name.split('/')[-1]
        )

    @staticmethod
    def localize_datetime(dt: datetime, timezone_name: str) -> datetime:
        """
        Attach timezone info to naive datetime.

        Args:
            dt: Datetime object (naive or aware)
            timezone_name: IANA timezone name

        Returns:
            Timezone-aware datetime

        Example:
            >>> dt = datetime(2024, 1, 15, 10, 0, 0)
            >>> aware_dt = TimezoneHandler.localize_datetime(dt, "Europe/Paris")
            >>> aware_dt.tzinfo is not None
            True
        """
        if dt.tzinfo is not None:
            return dt

        tz = ZoneInfo(timezone_name)
        return dt.replace(tzinfo=tz)

    @staticmethod
    def get_unique_timezones(events: list) -> Set[str]:
        """
        Extract unique timezone names from a list of events.

        Args:
            events: List of CalendarEvent objects

        Returns:
            Set of unique timezone names

        Example:
            >>> events = [event1, event2]  # doctest: +SKIP
            >>> timezones = TimezoneHandler.get_unique_timezones(events)
            >>> "UTC" in timezones
            True
        """
        timezones = set()
        for event in events:
            if hasattr(event, "timezone") and event.timezone:
                timezones.add(event.timezone)
        return timezones
