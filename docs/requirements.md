# ICalendar Builder - Requirements Specification

## Document Information

**Version:** 1.0
**Date:** 2025-01-01
**Status:** Draft

## 1. Project Overview

### 1.1 Purpose

The ICalendar Builder is a Python library designed to generate RFC 5545-compliant ICS (iCalendar) calendar files from structured event data. The library provides a type-safe, validated approach to creating calendar files for sporting events, festivals, conferences, and other event series.

### 1.2 Target Users

- **Orchestration Software**: Primary use case - automated systems that generate calendars from data pipelines
- **Python Developers**: Secondary use case - developers building event management systems
- **Data Engineers**: Tertiary use case - ETL pipelines that produce calendar outputs

### 1.3 Out of Scope

- Command-line interface (CLI) - not needed for orchestration
- Web UI or REST API
- Calendar synchronization or server-side storage
- Email integration or event invitations
- Import/parsing of existing ICS files (future enhancement)

## 2. Functional Requirements

### 2.1 Core Functionality

#### FR-1: Event Data Input

**Priority:** CRITICAL
**Description:** Accept event data in standardized JSON format

**Acceptance Criteria:**
- Support JSON file input
- Support Python dictionary input
- Validate all input against defined schema
- Provide clear error messages for invalid input
- Support nested event collections

#### FR-2: ICS File Generation

**Priority:** CRITICAL
**Description:** Generate RFC 5545-compliant ICS calendar files

**Acceptance Criteria:**
- Generate valid VCALENDAR components
- Generate valid VEVENT components
- Support both combined calendar files and individual event files
- Properly format all datetime values
- Include required ICS properties (UID, DTSTAMP, etc.)

#### FR-3: Template System

**Priority:** HIGH
**Description:** Support flexible template-based event formatting

**Acceptance Criteria:**
- Provide multiple built-in templates (standard, sport, music, recurring)
- Support custom user-provided templates
- Use Jinja2 for template rendering
- Allow template inheritance and composition
- Package built-in templates with the library

#### FR-4: Timezone Handling

**Priority:** CRITICAL
**Description:** Proper timezone support for international events

**Acceptance Criteria:**
- Support all IANA timezone identifiers
- Generate proper VTIMEZONE components
- Handle DST transitions automatically
- Allow per-event timezone specification
- Default to UTC if no timezone specified

#### FR-5: Event Validation

**Priority:** HIGH
**Description:** Validate event data before and after generation

**Acceptance Criteria:**
- Validate event data against Pydantic models
- Validate generated ICS files for RFC 5545 compliance
- Provide detailed validation error messages
- Allow optional validation bypass for performance
- Validate datetime ranges (end > start)

### 2.2 Event Types and Features

#### FR-6: Single Events

**Priority:** CRITICAL
**Description:** Support standard single-occurrence events

**Acceptance Criteria:**
- Start datetime (required)
- End datetime OR duration (one required)
- Summary/title (required)
- Description (optional)
- Location (optional)
- Status: TENTATIVE, CONFIRMED, CANCELLED

#### FR-7: Multi-day Events

**Priority:** HIGH
**Description:** Support events spanning multiple days

**Acceptance Criteria:**
- Start date different from end date
- All-day event support
- Proper duration calculation
- Timezone-aware multi-day handling

#### FR-8: Recurring Events

**Priority:** MEDIUM
**Description:** Support recurring event patterns

**Acceptance Criteria:**
- RRULE support for recurrence patterns
- Frequency: DAILY, WEEKLY, MONTHLY, YEARLY
- Count-based recurrence (N occurrences)
- Until-based recurrence (until date)
- By-day rules (e.g., every Monday)
- By-month-day rules

#### FR-9: Event Metadata

**Priority:** MEDIUM
**Description:** Support rich event metadata

**Acceptance Criteria:**
- Organizer information (name, email)
- Attendees list with roles (required, optional, chair)
- Categories/tags
- Priority levels (0-9)
- URL association
- Custom X-properties for extensibility

#### FR-10: Alarms/Reminders

**Priority:** LOW
**Description:** Support event alarms and reminders

**Acceptance Criteria:**
- Multiple alarms per event
- Display, email, and audio alarm types
- Trigger time specification (relative to event)
- Alarm descriptions
- Repeat configuration

### 2.3 Data Model Requirements

#### FR-11: Type Safety

**Priority:** HIGH
**Description:** Provide strongly-typed data models

**Acceptance Criteria:**
- Use Pydantic for all data models
- Full type hints throughout codebase
- Pass mypy strict mode checks
- Runtime type validation
- IDE autocomplete support

#### FR-12: JSON Schema

**Priority:** MEDIUM
**Description:** Provide JSON schemas for validation

**Acceptance Criteria:**
- JSON Schema for single events
- JSON Schema for calendar collections
- Schema versioning
- Documentation of schema fields
- Examples for each schema

### 2.4 Output Requirements

#### FR-13: Combined Calendar Output

**Priority:** CRITICAL
**Description:** Generate single ICS file with all events

**Acceptance Criteria:**
- Single VCALENDAR container
- Multiple VEVENT components
- One VTIMEZONE per unique timezone
- Proper PRODID field
- Configurable calendar name

#### FR-14: Individual Event Output

**Priority:** HIGH
**Description:** Generate separate ICS file per event

**Acceptance Criteria:**
- One file per event
- Configurable filename pattern
- Automatic directory creation
- Return list of generated file paths
- Preserve event ordering

#### FR-15: UID Generation

**Priority:** HIGH
**Description:** Generate unique event identifiers

**Acceptance Criteria:**
- Auto-generate UIDs if not provided
- UUID-based generation
- Include domain/namespace
- Ensure uniqueness within calendar
- Allow user-provided UIDs

### 2.5 Error Handling

#### FR-16: Validation Errors

**Priority:** HIGH
**Description:** Clear error messages for invalid input

**Acceptance Criteria:**
- Specific error types (ValidationError, TimezoneError, etc.)
- Include field name and invalid value in error
- Suggest corrections where possible
- Aggregate multiple validation errors
- Preserve stack traces for debugging

#### FR-17: File I/O Errors

**Priority:** MEDIUM
**Description:** Handle file operations gracefully

**Acceptance Criteria:**
- Check directory permissions before writing
- Handle disk full scenarios
- Provide clear error for missing input files
- Support atomic file writes
- Cleanup on failure

## 3. Technical Requirements

### 3.1 Platform Requirements

#### TR-1: Python Version

**Priority:** CRITICAL
**Requirement:** Python 3.10 or higher

**Rationale:**
- Modern type hints (PEP 604 union syntax)
- Pattern matching support
- Performance improvements
- zoneinfo standard library module

#### TR-2: Operating Systems

**Priority:** HIGH
**Requirement:** Cross-platform support (Linux, macOS, Windows)

**Rationale:**
- Orchestration software runs on diverse platforms
- Use pathlib for cross-platform paths
- No OS-specific dependencies

### 3.2 Dependencies

#### TR-3: Core Dependencies

**Priority:** CRITICAL
**Required Libraries:**
- `pydantic >= 2.0` - Data validation and models
- `jinja2 >= 3.1` - Template rendering
- `python-dateutil >= 2.8` - Date parsing utilities

**Optional Libraries:**
- `icalendar >= 5.0` - ICS validation (dev/test)

#### TR-4: Development Dependencies

**Priority:** HIGH
**Required Libraries:**
- `pytest >= 8.0` - Testing framework
- `pytest-cov >= 4.1` - Coverage reporting
- `pytest-mock >= 3.12` - Mocking support
- `ruff >= 0.3` - Linting and formatting
- `mypy >= 1.10` - Type checking
- `hatch` - Build and environment management

### 3.3 Performance Requirements

#### TR-5: Generation Speed

**Priority:** MEDIUM
**Requirement:** Generate 1000 events in < 1 second

**Rationale:**
- Orchestration systems may generate large calendars
- Batch processing should not be bottleneck
- Template caching for performance

#### TR-6: Memory Usage

**Priority:** MEDIUM
**Requirement:** < 100MB memory for 10,000 events

**Rationale:**
- Efficient for large event series
- Streaming generation if needed
- No unnecessary data duplication

#### TR-7: Startup Time

**Priority:** LOW
**Requirement:** Import time < 100ms

**Rationale:**
- Fast startup for orchestration scripts
- Lazy import of heavy dependencies
- Minimal initialization overhead

### 3.4 Code Quality Requirements

#### TR-8: Test Coverage

**Priority:** HIGH
**Requirement:** Minimum 90% code coverage

**Test Types:**
- Unit tests for all public APIs
- Integration tests for file generation
- Property-based tests for datetime handling
- Fixtures for common event types

#### TR-9: Type Checking

**Priority:** HIGH
**Requirement:** 100% mypy strict compliance

**Configuration:**
- Enable all strict flags
- No `type: ignore` comments without justification
- Type stubs for all public APIs

#### TR-10: Code Style

**Priority:** MEDIUM
**Requirement:** Consistent code formatting

**Tools:**
- Ruff for linting and formatting
- 100 character line length
- Follow PEP 8 conventions
- Docstrings for all public APIs

#### TR-11: Documentation

**Priority:** MEDIUM
**Requirement:** Comprehensive documentation

**Coverage:**
- API reference for all public interfaces
- Type hints serve as inline documentation
- Usage examples for common patterns
- Architecture documentation
- JSON schema documentation

### 3.5 Package Structure

#### TR-12: Hatch-based Build

**Priority:** HIGH
**Requirement:** Use Hatch for project management

**Rationale:**
- Consistent with mountainash-constants reference
- Modern Python packaging
- Virtual environment management
- Build script support

#### TR-13: Package Layout

**Priority:** HIGH
**Requirement:** src/ layout with proper namespacing

**Structure:**
```
src/icalendar_builder/
├── __init__.py      # Public API exports
├── builder.py       # CalendarBuilder class
├── models.py        # Pydantic models
├── templates/       # Template system
├── generators/      # ICS generation
├── validators/      # Validation logic
└── utils/           # Utilities
```

#### TR-14: Semantic Versioning

**Priority:** HIGH
**Requirement:** Follow semver for releases

**Format:** MAJOR.MINOR.PATCH
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## 4. Data Format Specifications

### 4.1 Input Data Format

#### JSON Event Structure

**Minimum Valid Event:**
```json
{
  "summary": "Event Title",
  "start": "2024-06-29T09:00:00",
  "end": "2024-06-29T17:00:00"
}
```

**Complete Event:**
```json
{
  "summary": "Tour de France Stage 1",
  "start": "2024-06-29T09:00:00",
  "end": "2024-06-29T17:00:00",
  "description": "Stage 1: Florence to Rimini (205 km)",
  "location": "Florence, Italy",
  "timezone": "Europe/Paris",
  "uid": "tdf-2024-stage-1@example.com",
  "organizer": {
    "name": "Tour de France",
    "email": "info@letour.fr"
  },
  "attendees": [
    {
      "email": "viewer@example.com",
      "name": "John Doe",
      "role": "OPT-PARTICIPANT",
      "rsvp": false
    }
  ],
  "categories": ["Sports", "Cycling"],
  "status": "CONFIRMED",
  "priority": 5,
  "url": "https://www.letour.fr/en/stage-1",
  "custom_properties": {
    "X-BROADCAST": "SBS",
    "X-DISTANCE": "205km"
  }
}
```

**Calendar Collection:**
```json
{
  "calendar_name": "Tour de France 2024",
  "calendar_description": "Complete schedule",
  "timezone": "Europe/Paris",
  "product_id": "//My App//Tour de France 2024//EN",
  "events": [
    {
      "summary": "Stage 1",
      "start": "2024-06-29T09:00:00",
      "end": "2024-06-29T17:00:00"
    }
  ]
}
```

### 4.2 Output Format

#### ICS File Structure

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID://icalendar-builder//EN
X-WR-CALNAME:Calendar Name
X-WR-TIMEZONE:Europe/Paris
BEGIN:VTIMEZONE
TZID:Europe/Paris
[...timezone definition...]
END:VTIMEZONE
BEGIN:VEVENT
UID:event-id@example.com
DTSTAMP:20240101T120000Z
DTSTART;TZID=Europe/Paris:20240629T090000
DTEND;TZID=Europe/Paris:20240629T170000
SUMMARY:Event Title
DESCRIPTION:Event description
LOCATION:Event location
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR
```

## 5. API Requirements

### 5.1 Public API

#### Core Classes
- `CalendarBuilder` - Main builder interface
- `CalendarEvent` - Event data model
- `CalendarCollection` - Collection data model
- `TemplateManager` - Template management
- `EventFactory` - Factory for common event types

#### Exception Classes
- `ICSBuilderError` - Base exception
- `ValidationError` - Invalid data
- `TemplateError` - Template rendering error
- `TimezoneError` - Invalid timezone

### 5.2 API Stability

**Guarantee:** Semantic versioning for public APIs
**Deprecation Policy:** 2 minor versions warning before removal
**Internal APIs:** Prefix with `_`, no stability guarantee

## 6. Compatibility Requirements

### 6.1 RFC 5545 Compliance

**Priority:** CRITICAL
**Requirement:** Generate valid RFC 5545 iCalendar files

**Validation:**
- Required properties present
- Proper line folding (75 characters)
- Correct datetime formats
- Valid RRULE syntax
- Proper escaping of special characters

### 6.2 Calendar Application Compatibility

**Priority:** HIGH
**Target Applications:**
- Google Calendar
- Apple Calendar
- Microsoft Outlook
- Mozilla Thunderbird

**Testing:** Manual import testing with each application

## 7. Non-Functional Requirements

### 7.1 Maintainability

- Clear separation of concerns
- Single responsibility principle
- DRY (Don't Repeat Yourself)
- Comprehensive tests
- Type safety throughout

### 7.2 Extensibility

- Template system for custom formats
- Custom properties support (X-*)
- Plugin architecture for validators (future)
- Easy to subclass and extend

### 7.3 Usability (for orchestration)

- Simple programmatic API
- Method chaining support
- Context manager support
- Sensible defaults
- Fail fast with clear errors

### 7.4 Security

- No code execution in templates (use safe Jinja2 config)
- Validate file paths (prevent directory traversal)
- No external network calls
- Sanitize user input in templates

## 8. Migration Requirements

### 8.1 Legacy Data Support

**Requirement:** Provide migration tool for old format

**Old Format:**
```python
[
    {
        "start_date": "20240629",
        "end_date": "20240629",
        "start_time": "0900",
        "end_time": "1700",
        "description": "Event Name"
    }
]
```

**Migration Function:**
```python
def migrate_legacy_format(
    old_events: list[dict],
    timezone: str = "UTC"
) -> dict:
    """Convert legacy format to new JSON schema."""
    ...
```

## 9. Future Enhancements (Not in v1.0)

### 9.1 Potential Features

- Import/parse existing ICS files
- Calendar diff/merge operations
- Integration with external APIs (Google Calendar, etc.)
- CLI tool (if demand emerges)
- Web-based calendar viewer
- ICS to JSON conversion
- Batch processing optimizations
- Async I/O support

### 9.2 Template Enhancements

- Template marketplace/registry
- Visual template builder
- Template validation and testing
- More built-in templates
- Template documentation generator

## 10. Acceptance Criteria

### 10.1 Definition of Done

A feature is considered complete when:

1. Implementation complete and code reviewed
2. Unit tests written (90%+ coverage)
3. Integration tests pass
4. Type checking passes (mypy strict)
5. Linting passes (ruff)
6. Documentation updated
7. Examples provided
8. Manually tested with real calendar apps

### 10.2 Release Criteria

Version 1.0 can be released when:

1. All CRITICAL priority requirements implemented
2. All HIGH priority requirements implemented
3. 90%+ test coverage achieved
4. Documentation complete
5. Manual testing with major calendar apps successful
6. Performance benchmarks met
7. Security review completed

## Appendix A: Glossary

- **ICS**: iCalendar file format (.ics extension)
- **RFC 5545**: Internet standard for iCalendar format
- **VEVENT**: Calendar component representing an event
- **VCALENDAR**: Top-level calendar container
- **VTIMEZONE**: Timezone definition component
- **UID**: Unique identifier for calendar components
- **RRULE**: Recurrence rule defining recurring events
- **IANA**: Internet Assigned Numbers Authority (timezone database)
- **Orchestration**: Automated workflow/pipeline systems

## Appendix B: References

- RFC 5545: https://tools.ietf.org/html/rfc5545
- iCalendar.org: https://icalendar.org/
- Pydantic Documentation: https://docs.pydantic.dev/
- Hatch Documentation: https://hatch.pypa.io/
- IANA Time Zones: https://www.iana.org/time-zones
