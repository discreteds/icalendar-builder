#!/usr/bin/env python3
"""
Example: Standard Template
===========================

Demonstrates the standard template for general business and personal events.
This template includes all available fields: organizers, attendees, alarms,
priorities, URLs, and custom properties.
"""

from datetime import datetime, timedelta
from icalendar_builder import CalendarBuilder, EventFactory
from icalendar_builder.models import Organizer, Attendee, Alarm, AttendeeRole, AlarmAction


def main():
    """Create a business calendar with various event types."""
    print("Standard Template Example")
    print("=" * 50)

    # Create calendar
    builder = CalendarBuilder(
        calendar_name="Q1 Business Events",
        timezone="America/New_York",
        template="standard"
    )

    # Example 1: Team meeting with organizer and attendees
    print("\n1. Team meeting with attendees...")
    start = datetime(2024, 1, 15, 14, 0, 0)
    end = datetime(2024, 1, 15, 15, 0, 0)

    builder.add_event(
        summary="Q1 Planning Meeting",
        start=start,
        end=end,
        description="Quarterly planning session for Q1 2024 goals and objectives",
        location="Conference Room B",
        organizer=Organizer(
            email="manager@company.com",
            name="Sarah Manager"
        ),
        attendees=[
            Attendee(
                email="john@company.com",
                name="John Developer",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="jane@company.com",
                name="Jane Designer",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="bob@company.com",
                name="Bob Consultant",
                role=AttendeeRole.OPTIONAL,
                rsvp=False
            ),
        ],
        alarms=[
            Alarm(
                action=AlarmAction.DISPLAY,
                trigger="-PT15M",
                description="Meeting starts in 15 minutes"
            ),
        ],
        url="https://meet.company.com/q1-planning",
        categories=["Business", "Planning"]
    )

    # Example 2: High-priority deadline
    print("2. High-priority deadline...")
    deadline = datetime(2024, 1, 20, 17, 0, 0)

    builder.add_event(
        summary="Project Alpha Delivery Deadline",
        start=deadline,
        duration="PT1H",
        description="Final deliverables must be submitted by 5 PM",
        priority=1,  # High priority
        alarms=[
            Alarm(
                action=AlarmAction.DISPLAY,
                trigger="-P1D",
                description="Deadline tomorrow!"
            ),
            Alarm(
                action=AlarmAction.DISPLAY,
                trigger="-PT2H",
                description="Deadline in 2 hours"
            ),
        ],
        categories=["Deadline", "Project Alpha"],
        custom_properties={
            "X-PROJECT-ID": "ALPHA-2024",
            "X-DEPARTMENT": "Engineering"
        }
    )

    # Example 3: Client presentation with URL
    print("3. Client presentation...")
    presentation_start = datetime(2024, 1, 25, 10, 0, 0)

    builder.add_event(
        summary="Client Demo - Product Launch",
        start=presentation_start,
        duration="PT2H",
        description="Product demonstration for Acme Corp. Include Q&A session.",
        location="Virtual - Zoom",
        organizer=Organizer(
            email="sales@company.com",
            name="Sales Team"
        ),
        attendees=[
            Attendee(
                email="client@acmecorp.com",
                name="Client Representative",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
        ],
        url="https://zoom.us/j/123456789",
        alarms=[
            Alarm(
                action=AlarmAction.DISPLAY,
                trigger="-PT30M",
                description="Join the call in 30 minutes"
            ),
        ],
        categories=["Sales", "Demo"],
        custom_properties={
            "X-CLIENT": "Acme Corp",
            "X-ZOOM-ID": "123456789"
        }
    )

    # Example 4: All-day event
    print("4. All-day company event...")
    event_day = datetime(2024, 1, 31, 0, 0, 0)

    builder.add_event(
        summary="Company All-Hands Meeting",
        start=event_day,
        duration="P1D",  # Full day
        description="Annual company-wide meeting and celebration",
        location="Main Office - Auditorium",
        categories=["Company", "All-Hands"],
        custom_properties={
            "X-EVENT-TYPE": "Company-Wide"
        }
    )

    # Generate output
    print("\nGenerating calendar files...")
    output_file = "examples/output/standard_business_calendar.ics"
    builder.save(output_file)
    print(f"✓ Created: {output_file}")

    # Also create individual event files
    builder.save_individual_events("examples/output/standard_events")
    print("✓ Created individual event files in: examples/output/standard_events/")

    print("\n" + "=" * 50)
    print("Standard template example complete!")
    print(f"Calendar contains {len(builder.events)} events")
    print("\nFeatures demonstrated:")
    print("  • Organizers and attendees with RSVP")
    print("  • Multiple alarms per event")
    print("  • Event priorities")
    print("  • URLs for virtual meetings")
    print("  • Custom properties (X- extensions)")
    print("  • Categories for organization")
    print("  • Both duration and end time formats")


if __name__ == "__main__":
    main()
