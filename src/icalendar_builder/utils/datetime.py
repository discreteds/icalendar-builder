"""DateTime utilities for calendar event handling."""

import re
from datetime import datetime, timedelta
from typing import Optional, Union

from dateutil.parser import parse as dateutil_parse


class DateTimeUtils:
    """DateTime handling utilities."""

    @staticmethod
    def parse_datetime(dt_input: Union[str, datetime], timezone: Optional[str] = None) -> datetime:
        """
        Parse datetime string to datetime object.

        Supports:
        - ISO 8601: 2024-06-29T09:00:00
        - ICS format: 20240629T090000
        - Date only: 2024-06-29 (assumes midnight)

        Args:
            dt_input: Datetime string or datetime object
            timezone: Optional timezone name to apply

        Returns:
            Datetime object

        Example:
            >>> DateTimeUtils.parse_datetime("2024-01-15T10:00:00")
            datetime.datetime(2024, 1, 15, 10, 0)
        """
        if isinstance(dt_input, datetime):
            return dt_input

        # Try parsing with dateutil (handles most formats)
        dt = dateutil_parse(dt_input)

        # Apply timezone if specified and datetime is naive
        if timezone and dt.tzinfo is None:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(timezone))

        return dt

    @staticmethod
    def format_ics_datetime(dt: datetime) -> str:
        """
        Format datetime for ICS output (YYYYMMDDTHHmmss).

        Args:
            dt: Datetime object

        Returns:
            Formatted string

        Example:
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> DateTimeUtils.format_ics_datetime(dt)
            '20240115T103000'
        """
        return dt.strftime("%Y%m%dT%H%M%S")

    @staticmethod
    def calculate_duration(start: datetime, end: datetime) -> str:
        """
        Calculate ISO 8601 duration between datetimes.

        Returns: PTxHxMxS format

        Args:
            start: Start datetime
            end: End datetime

        Returns:
            ISO 8601 duration string

        Example:
            >>> start = datetime(2024, 1, 15, 10, 0, 0)
            >>> end = datetime(2024, 1, 15, 12, 30, 0)
            >>> DateTimeUtils.calculate_duration(start, end)
            'PT2H30M0S'
        """
        delta = end - start
        total_seconds = int(delta.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"PT{hours}H{minutes}M{seconds}S"

    @staticmethod
    def parse_duration(duration_str: str) -> timedelta:
        """
        Parse ISO 8601 duration to timedelta.

        Supports: PTxHxMxS format (hours, minutes, seconds)

        Args:
            duration_str: ISO 8601 duration string

        Returns:
            timedelta object

        Raises:
            ValueError: If duration format is invalid

        Example:
            >>> DateTimeUtils.parse_duration("PT2H30M0S")
            datetime.timedelta(seconds=9000)
        """
        # Pattern for PT format: PTxHxMxS
        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?"
        match = re.match(pattern, duration_str)

        if not match:
            raise ValueError(f"Invalid ISO 8601 duration: {duration_str}")

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = float(match.group(3) or 0)

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def format_datetime_with_tz(dt: datetime, timezone: str) -> str:
        """
        Format datetime with timezone for ICS (DTSTART;TZID=...:...).

        Args:
            dt: Datetime object
            timezone: IANA timezone name

        Returns:
            Formatted datetime string

        Example:
            >>> dt = datetime(2024, 1, 15, 10, 0, 0)
            >>> DateTimeUtils.format_datetime_with_tz(dt, "Europe/Paris")
            '20240115T100000'
        """
        # Apply timezone if datetime is naive
        if dt.tzinfo is None:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(timezone))

        return dt.strftime("%Y%m%dT%H%M%S")
