"""Base template classes for ICS generation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Protocol

from jinja2 import Environment, FileSystemLoader

from ..models import CalendarEvent


class TemplateProtocol(Protocol):
    """Protocol defining template interface."""

    def render(self, event: CalendarEvent) -> str:
        """Render event to ICS format."""
        ...


class BaseTemplate(ABC):
    """Base template class for ICS generation."""

    def __init__(self, template_path: Optional[Path] = None) -> None:
        self.template_path = template_path
        self._template_content: Optional[str] = None

    @abstractmethod
    def render(self, event: CalendarEvent) -> str:
        """Render event to ICS VEVENT component."""
        pass

    def load_template(self) -> str:
        """Load template from file."""
        if self._template_content is None and self.template_path:
            with open(self.template_path, "r") as f:
                self._template_content = f.read()
        return self._template_content or ""


class Jinja2Template(BaseTemplate):
    """Template using Jinja2 rendering engine."""

    def __init__(self, template_path: Path) -> None:
        super().__init__(template_path)

        # Configure Jinja2 for ICS generation
        self.env = Environment(
            loader=FileSystemLoader(template_path.parent),
            autoescape=False,  # ICS not HTML
            trim_blocks=True,  # Clean whitespace
            lstrip_blocks=True,  # Clean indentation
        )

        # Register custom filters
        self.env.filters["fold_text"] = self._fold_text
        self.env.filters["escape_text"] = self._escape_text
        self.env.filters["datetime_format"] = self._datetime_format

        self.template = self.env.get_template(template_path.name)

    def render(self, event: CalendarEvent) -> str:
        """Render event using Jinja2 template."""
        context = event.model_dump(mode='json')
        rendered = self.template.render(event=context)
        # Ensure consistent line endings (RFC 5545 requires \r\n)
        rendered = rendered.replace('\r\n', '\n').replace('\n', '\r\n')
        return rendered

    @staticmethod
    def _fold_text(text: str, width: int = 75) -> str:
        """
        Fold long lines per RFC 5545 (75 char limit).

        Lines longer than width are broken and continued with a space on the next line.
        """
        if not text or len(text) <= width:
            return text

        lines = []
        while len(text) > width:
            lines.append(text[:width])
            text = text[width:]

        if text:
            lines.append(text)

        return "\r\n ".join(lines)

    @staticmethod
    def _escape_text(text: str) -> str:
        """
        Escape special characters for ICS format.

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

    @staticmethod
    def _datetime_format(dt: object, tz_format: bool = False) -> str:
        """
        Format datetime for ICS output (YYYYMMDDTHHmmss).

        Args:
            dt: Datetime object (or string if already formatted)
            tz_format: If True, return in timezone format (TZID:...)
        """
        from datetime import datetime

        if isinstance(dt, str):
            return dt

        if isinstance(dt, datetime):
            return dt.strftime("%Y%m%dT%H%M%S")

        # Fallback for other types
        return str(dt)
