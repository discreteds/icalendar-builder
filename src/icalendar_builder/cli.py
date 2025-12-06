"""
Command-line interface for icalendar-builder.

Generate ICS calendar files from JSON event data.

Usage:
    icalendar-builder --name "Calendar" --timezone "UTC" --output calendar.ics --events-file events.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .builder import CalendarBuilder


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="icalendar-builder",
        description="Generate ICS calendar files from event data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # From JSON file
    icalendar-builder \\
        --name "My Calendar" \\
        --timezone "Australia/Melbourne" \\
        --output my_calendar.ics \\
        --events-file events.json

    # With template and custom reminder
    icalendar-builder \\
        --name "Concert Schedule" \\
        --timezone "America/New_York" \\
        --template music \\
        --reminder-minutes 30 \\
        --output concerts.ics \\
        --events-file concerts.json

    # No reminders
    icalendar-builder \\
        --name "Tour de France 2025" \\
        --timezone "Europe/Paris" \\
        --template sport \\
        --no-reminder \\
        --output tdf.ics \\
        --events-file stages.json

    # Individual event files
    icalendar-builder \\
        --name "Festival Schedule" \\
        --timezone "Australia/Melbourne" \\
        --template music \\
        --output events/ \\
        --events-file schedule.json \\
        --individual
        """
    )

    parser.add_argument(
        "--name", "-n",
        required=True,
        help="Calendar name (appears in calendar apps)"
    )

    parser.add_argument(
        "--timezone", "-tz",
        default="UTC",
        help="IANA timezone identifier (default: UTC)"
    )

    parser.add_argument(
        "--template", "-t",
        default="standard",
        choices=["standard", "sport", "music", "recurring"],
        help="Event template type (default: standard)"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output ICS file path"
    )

    # Event data source (mutually exclusive)
    event_source = parser.add_mutually_exclusive_group(required=True)
    event_source.add_argument(
        "--events-json", "-j",
        help="JSON string containing events"
    )
    event_source.add_argument(
        "--events-file", "-f",
        help="Path to JSON file containing events"
    )

    parser.add_argument(
        "--individual", "-i",
        action="store_true",
        help="Save each event as a separate file"
    )

    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip ICS validation"
    )

    # Reminder configuration
    reminder_group = parser.add_mutually_exclusive_group()
    reminder_group.add_argument(
        "--reminder",
        action="store_true",
        default=None,
        help="Enable reminders (default: enabled)"
    )
    reminder_group.add_argument(
        "--no-reminder",
        action="store_true",
        help="Disable reminders"
    )

    parser.add_argument(
        "--reminder-minutes",
        type=int,
        metavar="MINS",
        help="Minutes before event for reminder (default: template-based - music: 15, sport: 30, standard/recurring: 60)"
    )

    return parser.parse_args(args)


def load_events(args: argparse.Namespace) -> list[dict[str, Any]]:
    """Load events from JSON string or file."""
    if args.events_json:
        try:
            data = json.loads(args.events_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        events_path = Path(args.events_file)
        if not events_path.exists():
            print(f"Error: Events file not found: {events_path}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(events_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}", file=sys.stderr)
            sys.exit(1)

    # Support both {"events": [...]} and direct list format
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "events" in data:
        return data["events"]
    else:
        print("Error: JSON must be a list of events or an object with 'events' key", file=sys.stderr)
        sys.exit(1)


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)

    # Load events
    events = load_events(parsed_args)

    if not events:
        print("Error: No events provided", file=sys.stderr)
        return 1

    # Determine reminder setting
    # --no-reminder explicitly disables, --reminder explicitly enables, neither = default (True)
    if parsed_args.no_reminder:
        default_reminder = False
    elif parsed_args.reminder:
        default_reminder = True
    else:
        default_reminder = None  # Use builder default (True)

    # Create builder
    try:
        builder = CalendarBuilder(
            calendar_name=parsed_args.name,
            timezone=parsed_args.timezone,
            template=parsed_args.template,
            validate=not parsed_args.no_validate,
            default_reminder=default_reminder,
            reminder_minutes=parsed_args.reminder_minutes,
        )
    except Exception as e:
        print(f"Error creating calendar builder: {e}", file=sys.stderr)
        return 1

    # Add events
    for i, event in enumerate(events, 1):
        try:
            builder.add_event(**event)
        except Exception as e:
            print(f"Error adding event {i}: {e}", file=sys.stderr)
            print(f"Event data: {event}", file=sys.stderr)
            return 1

    # Generate output
    output_path = Path(parsed_args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if parsed_args.individual:
            files = builder.save_individual_events(
                output_dir=output_path.parent,
                filename_template="{index:02d}_{summary}.ics"
            )
            print(f"Created {len(files)} individual event files in: {output_path.parent}")
            for f in files:
                print(f"  - {f.name}")
        else:
            saved_path = builder.save(output_path)
            print(f"Calendar created successfully: {saved_path}")
            print(f"  Events: {len(builder)}")
            print(f"  Timezone: {parsed_args.timezone}")
            print(f"  Template: {parsed_args.template}")
    except Exception as e:
        print(f"Error saving calendar: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
