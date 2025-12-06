# ICalendar Builder

Modern Python library for generating ICS calendar files with type safety and validation.

## Features

- **Type-Safe**: Full Pydantic validation with type hints
- **RFC 5545 Compliant**: Generate valid ICS calendar files
- **Flexible Templates**: Built-in templates for common event types
- **Timezone Support**: All IANA timezones supported
- **Rich Event Types**: Single events, recurring events, alarms, attendees
- **Orchestration-Friendly**: JSON-driven configuration for automation

## Installation

```bash
pip install icalendar-builder
```

## Quick Start

```python
from icalendar_builder import CalendarBuilder

# Simple usage
builder = CalendarBuilder(timezone="Europe/Paris")
builder.add_event(
    summary="Team Meeting",
    start="2024-01-15T10:00:00",
    end="2024-01-15T11:00:00"
)
builder.save("meeting.ics")

# From JSON
CalendarBuilder.from_json("events.json").save("calendar.ics")
```

## Requirements

- Python 3.10+
- Pydantic 2.0+
- Jinja2 3.1+

## Documentation

See `docs/` directory for comprehensive documentation:

- `docs/requirements.md` - Functional and technical requirements
- `docs/architecture.md` - System architecture and design
- `docs/api_design.md` - Complete API reference with examples
- `docs/implementation_plan.md` - Development roadmap

## Development

```bash
# Setup development environment
hatch env create

# Run tests
hatch run test:test

# Run linting
hatch run ruff:check

# Type checking
hatch run mypy:check
```

## License

MIT License - See LICENSE file for details

## Status

This project is currently in development (v0.1.0).
