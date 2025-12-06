# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based calendar event generator that creates ICS (iCalendar) files for sporting events and festivals. The tool generates both individual event files and combined calendar files that can be imported into calendar applications.

## Core Architecture

### CalendarBuilder Class (`src/ics_generator.py`)

The main class that handles all calendar generation logic:

- **Initialization**: Takes title, events, template file path, output directory, and timezone
- **Template-based generation**: Uses text template files from `config/` directory to generate ICS files
- **Dual output mode**: Creates both individual event files (`event1.ics`, `event2.ics`, etc.) and a combined calendar file

### Event Data Structure

The codebase uses two different event data formats:

**Legacy format** (seen in `ics_generator.ipynb`):
```python
events = [
    {"date": "20230701", "description": "Stage 1: ..."},
    ...
]
```

**Modern format** (seen in `tdf_2024.ipynb`):
```python
events = {
  "general_details": {
    "calendar_title": "...",
    "calendar_timezone": "..."
  },
  "event_details": [
    {
      "start_date": "20240629",
      "end_date": "20240629",
      "start_time": "0900",
      "end_time": "1700",
      "description": "..."
    },
    ...
  ]
}
```

The modern format supports duration calculation via `format_duration()` method.

## Usage Pattern

Typical workflow executed in Jupyter notebooks (`notebooks/`):

1. Import the `CalendarBuilder` class
2. Define event data (dates, times, descriptions)
3. Specify template file from `config/` directory
4. Instantiate `CalendarBuilder` with title, events, template, and output directory
5. Call `create_ics_files()` to generate individual event files
6. Call `combine_ics_files(outputfile="name.ics")` to create combined calendar

## Key Methods

- `create_ics_files()`: Generates individual ICS files for each event in the `output_directory`
- `combine_ics_files(outputfile)`: Merges all individual ICS files into a single combined calendar file
- `format_duration(start, end)`: Calculates ISO 8601 duration from start/end timestamps

## Directory Structure

- `src/`: Contains the `CalendarBuilder` class implementation
- `config/`: ICS template files for different event types (Tour de France, FIFA Women's World Cup, Ashes, Golden Plains festival, etc.)
- `notebooks/`: Jupyter notebooks that use the CalendarBuilder to generate calendars for specific events
- `outputs/`: Generated ICS files organized by event (created at runtime)

## Templates

ICS templates in `config/` use Python string formatting with placeholders like:
- `{timezone}`: Timezone identifier
- `{title}`: Calendar title
- `{stage_number}` or `{event_number}`: Sequential event number
- `{date}`, `{start_date}`, `{end_date}`: Date values
- `{start_time}`, `{end_time}`: Time values
- `{description}`: Event description
- `{duration}`: Calculated ISO 8601 duration

## Running the Code

This project uses Jupyter notebooks as the primary interface. To generate calendars:

```bash
# Launch Jupyter
jupyter notebook

# Open a notebook from notebooks/ directory
# Run all cells to generate calendar files
```

To use programmatically in Python:
```python
from src.ics_generator import CalendarBuilder

calendar = CalendarBuilder(
    title="Event Title",
    events=event_data,
    template_file="config/template.txt",
    output_directory="outputs/event_name"
)
calendar.create_ics_files()
calendar.combine_ics_files(outputfile="combined.ics")
```

## Hardcoded Timezone in combine_ics_files()

The `combine_ics_files()` method hardcodes Australia/Melbourne timezone in the VTIMEZONE section (lines 70-89 of `src/ics_generator.py`). This is inconsistent with the configurable timezone used elsewhere and should be addressed during modernization.
