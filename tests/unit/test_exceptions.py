"""Unit tests for exception classes."""

import pytest
from pathlib import Path

from icalendar_builder.exceptions import (
    FileIOError,
    GenerationError,
    ICSBuilderError,
    TemplateError,
    TimezoneError,
    ValidationError,
)


class TestICSBuilderError:
    """Tests for base exception class."""

    def test_base_exception_creation(self):
        """Test creating base exception."""
        exc = ICSBuilderError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_without_field(self):
        """Test validation error without field."""
        exc = ValidationError("Invalid data")
        assert str(exc) == "Invalid data"
        assert exc.field is None

    def test_validation_error_with_field(self):
        """Test validation error with field."""
        exc = ValidationError("Invalid value", field="summary")
        assert str(exc) == "Invalid value"
        assert exc.field == "summary"

    def test_validation_error_is_ics_builder_error(self):
        """Test that ValidationError is subclass of ICSBuilderError."""
        exc = ValidationError("Test")
        assert isinstance(exc, ICSBuilderError)


class TestTemplateError:
    """Tests for TemplateError."""

    def test_template_error_creation(self):
        """Test creating template error."""
        exc = TemplateError("Template not found")
        assert str(exc) == "Template not found"
        assert isinstance(exc, ICSBuilderError)


class TestTimezoneError:
    """Tests for TimezoneError."""

    def test_timezone_error_default_message(self):
        """Test timezone error with default message."""
        exc = TimezoneError("Invalid/Timezone")
        assert "Invalid timezone: Invalid/Timezone" in str(exc)
        assert exc.timezone == "Invalid/Timezone"

    def test_timezone_error_custom_message(self):
        """Test timezone error with custom message."""
        exc = TimezoneError("Invalid/Timezone", "Custom error message")
        assert str(exc) == "Custom error message"
        assert exc.timezone == "Invalid/Timezone"

    def test_timezone_error_is_ics_builder_error(self):
        """Test that TimezoneError is subclass of ICSBuilderError."""
        exc = TimezoneError("Invalid/Timezone")
        assert isinstance(exc, ICSBuilderError)


class TestGenerationError:
    """Tests for GenerationError."""

    def test_generation_error_creation(self):
        """Test creating generation error."""
        exc = GenerationError("Failed to generate ICS")
        assert str(exc) == "Failed to generate ICS"
        assert isinstance(exc, ICSBuilderError)


class TestFileIOError:
    """Tests for FileIOError."""

    def test_file_io_error_creation(self):
        """Test creating file I/O error."""
        original_error = IOError("Permission denied")
        exc = FileIOError(
            path=Path("/tmp/test.ics"),
            operation="write",
            original_error=original_error,
        )

        assert "Failed to write file" in str(exc)
        assert "/tmp/test.ics" in str(exc)
        assert "Permission denied" in str(exc)
        assert exc.path == Path("/tmp/test.ics")
        assert exc.operation == "write"
        assert exc.original_error is original_error

    def test_file_io_error_is_ics_builder_error(self):
        """Test that FileIOError is subclass of ICSBuilderError."""
        exc = FileIOError(
            path=Path("/tmp/test.ics"),
            operation="write",
            original_error=IOError("Test"),
        )
        assert isinstance(exc, ICSBuilderError)
