"""Exception classes for icalendar-builder."""

from pathlib import Path
from typing import Optional


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

    def __init__(self, message: str, field: Optional[str] = None) -> None:
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

    def __init__(self, timezone: str, message: Optional[str] = None) -> None:
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

    def __init__(self, path: Path, operation: str, original_error: Exception) -> None:
        self.path = path
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Failed to {operation} file {path}: {original_error}")
