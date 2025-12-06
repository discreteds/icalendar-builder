"""Base generator interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from ..models import CalendarEvent


class BaseGenerator(ABC):
    """
    Abstract base for all generators.

    Defines the contract for ICS content generation.
    """

    @abstractmethod
    def generate(self, events: List[CalendarEvent]) -> str:
        """
        Generate ICS content from events.

        Args:
            events: List of calendar events

        Returns:
            ICS file content as string
        """
        pass

    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        """Format datetime for ICS output (YYYYMMDDTHHmmss)."""
        return dt.strftime("%Y%m%dT%H%M%S")

    @staticmethod
    def _escape_text(text: str) -> str:
        """
        Escape special ICS characters.

        RFC 5545 requires escaping: backslash, semicolon, comma, newline
        """
        if not text:
            return text

        # Order matters! Backslash first
        text = text.replace("\\", "\\\\")
        text = text.replace(";", "\\;")
        text = text.replace(",", "\\,")
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "")  # Remove carriage returns
        return text
