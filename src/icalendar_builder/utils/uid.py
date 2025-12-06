"""UID generation for calendar events."""

import uuid
from typing import Optional


class UIDGenerator:
    """Generate unique identifiers for events."""

    def __init__(self, domain: str = "icalendar-builder.local") -> None:
        """
        Initialize UID generator.

        Args:
            domain: Domain name to use in UIDs

        Example:
            >>> gen = UIDGenerator("example.com")
            >>> gen.domain
            'example.com'
        """
        self.domain = domain

    def generate(self, event_hint: Optional[str] = None) -> str:
        """
        Generate unique event UID.

        Creates a UUID-based UID in the format: {uuid}@{domain}

        Args:
            event_hint: Optional hint for UID (currently unused, reserved for future)

        Returns:
            Unique identifier string

        Example:
            >>> gen = UIDGenerator()
            >>> uid = gen.generate()
            >>> "@icalendar-builder.local" in uid
            True
            >>> len(uid.split("@")[0]) == 36  # UUID length
            True
        """
        uid = str(uuid.uuid4())
        return f"{uid}@{self.domain}"

    @staticmethod
    def validate_uid(uid: str) -> bool:
        """
        Validate UID format.

        UIDs should not contain whitespace or control characters.

        Args:
            uid: UID string to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> UIDGenerator.validate_uid("valid-uid@domain.com")
            True
            >>> UIDGenerator.validate_uid("invalid uid with spaces")
            False
        """
        if not uid:
            return False

        # Check for whitespace or control characters
        if any(c in uid for c in [" ", "\n", "\t", "\r"]):
            return False

        return True
