"""Basic usage example for icalendar-builder."""

from datetime import datetime
from icalendar_builder import CalendarBuilder, EventFactory

# Example 1: Simple calendar with one event
print("Example 1: Simple calendar")
print("-" * 50)

builder = CalendarBuilder(
    calendar_name="My Calendar",
    timezone="America/New_York"
)

builder.add_event(
    summary="Team Meeting",
    start="2024-01-15T10:00:00",
    end="2024-01-15T11:00:00",
    location="Conference Room A",
    description="Weekly team sync"
)

# Save the calendar
output_file = builder.save("examples/output/simple_calendar.ics")
print(f"✓ Created: {output_file}")
print(f"  Events: {len(builder)}")
print()


# Example 2: Method chaining
print("Example 2: Method chaining")
print("-" * 50)

(CalendarBuilder(timezone="UTC")
    .add_event(
        summary="Morning Standup",
        start="2024-01-15T09:00:00",
        duration="PT15M"
    )
    .add_event(
        summary="Lunch Break",
        start="2024-01-15T12:00:00",
        duration="PT1H"
    )
    .add_event(
        summary="Afternoon Review",
        start="2024-01-15T16:00:00",
        duration="PT30M"
    )
    .save("examples/output/daily_schedule.ics"))

print("✓ Created: examples/output/daily_schedule.ics")
print()


# Example 3: Using EventFactory
print("Example 3: EventFactory for common event types")
print("-" * 50)

builder = CalendarBuilder(timezone="Australia/Melbourne")

# Sport event
sport_event = EventFactory.sport_event(
    sport_name="Basketball",
    event_name="Finals Game 1",
    start=datetime(2024, 6, 6, 20, 30),
    duration="PT3H",
    location="Madison Square Garden"
)
builder.add_event(**sport_event.model_dump())

# Music event
music_event = EventFactory.music_event(
    artist="The Rolling Stones",
    venue="MetLife Stadium",
    start=datetime(2024, 8, 15, 19, 0),
    end=datetime(2024, 8, 15, 23, 0),
    ticket_url="https://tickets.example.com"
)
builder.add_event(**music_event.model_dump())

# Recurring meeting
meeting = EventFactory.recurring_meeting(
    summary="Weekly Team Sync",
    start=datetime(2024, 1, 8, 10, 0),
    duration="PT30M",
    frequency="WEEKLY",
    count=12,
    by_day=["MO"]
)
builder.add_event(**meeting.model_dump())

output_file = builder.save("examples/output/mixed_events.ics")
print(f"✓ Created: {output_file}")
print(f"  Events: {len(builder)}")
print()


# Example 4: Individual event files
print("Example 4: Individual event files")
print("-" * 50)

builder = CalendarBuilder(timezone="Europe/Paris")
builder.add_event(
    summary="Conference Day 1",
    start="2024-09-15T09:00:00",
    duration="PT8H"
)
builder.add_event(
    summary="Conference Day 2",
    start="2024-09-16T09:00:00",
    duration="PT8H"
)

individual_files = builder.save_individual_events(
    output_dir="examples/output/conference",
    filename_template="{index:02d}_{summary}.ics"
)

print(f"✓ Created {len(individual_files)} individual files:")
for f in individual_files:
    print(f"  - {f.name}")

print()
print("=" * 50)
print("All examples completed successfully!")
print("Check examples/output/ for generated ICS files")
