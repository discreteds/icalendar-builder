#!/usr/bin/env python3
"""
Example: Recurring Template
============================

Demonstrates the recurring template for repeating events: meetings, classes,
appointments, and regular activities. This template emphasizes recurrence rules,
organizers, and attendees for collaborative recurring events.
"""

from datetime import datetime
from icalendar_builder import CalendarBuilder, EventFactory
from icalendar_builder.models import (
    Recurrence, RecurrenceFrequency, Organizer, Attendee, AttendeeRole
)


def main():
    """Create calendars with various recurring event patterns."""
    print("Recurring Template Example")
    print("=" * 50)

    # Example 1: Weekly team meetings
    print("\n1. Weekly team standup...")
    weekly_builder = CalendarBuilder(
        calendar_name="Team Meetings",
        timezone="America/New_York",
        template="recurring"
    )

    weekly_builder.add_event(
        summary="Daily Standup",
        start=datetime(2024, 1, 8, 9, 0, 0),  # Monday
        duration="PT15M",
        description="Quick daily sync - What did you do? What will you do? Any blockers?",
        location="Conference Room A / Zoom",
        organizer=Organizer(
            email="scrum.master@company.com",
            name="Alice Scrum Master"
        ),
        attendees=[
            Attendee(
                email="dev1@company.com",
                name="Bob Developer",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="dev2@company.com",
                name="Carol Developer",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="designer@company.com",
                name="Dave Designer",
                role=AttendeeRole.OPTIONAL,
                rsvp=False
            ),
        ],
        recurrence=Recurrence(
            frequency=RecurrenceFrequency.DAILY,
            by_day=["MO", "TU", "WE", "TH", "FR"],  # Weekdays only
            count=60  # 3 months of standups
        ),
        categories=["Scrum", "Daily"]
    )

    # Example 2: Biweekly sprint planning
    print("2. Biweekly sprint planning...")
    weekly_builder.add_event(
        summary="Sprint Planning",
        start=datetime(2024, 1, 8, 14, 0, 0),
        duration="PT2H",
        description="Plan the next two-week sprint: review backlog, estimate stories, commit to sprint goals",
        location="Conference Room B",
        organizer=Organizer(
            email="scrum.master@company.com",
            name="Alice Scrum Master"
        ),
        attendees=[
            Attendee(
                email="product.owner@company.com",
                name="Eve Product Owner",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="dev1@company.com",
                name="Bob Developer",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="dev2@company.com",
                name="Carol Developer",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
        ],
        recurrence=Recurrence(
            frequency=RecurrenceFrequency.WEEKLY,
            interval=2,  # Every 2 weeks
            by_day=["MO"],  # Mondays
            count=12  # 6 months of sprints
        ),
        categories=["Scrum", "Planning"]
    )

    # Example 3: Monthly classes
    print("\n3. Monthly yoga classes...")
    class_builder = CalendarBuilder(
        calendar_name="Yoga Classes - Winter 2024",
        timezone="America/Los_Angeles",
        template="recurring"
    )

    class_builder.add_event(
        summary="Vinyasa Yoga Class",
        start=datetime(2024, 1, 10, 18, 30, 0),  # Wednesday
        duration="PT1H",
        description="All-levels Vinyasa flow class. Bring your own mat or rent one at the studio.",
        location="Yoga Studio Downtown",
        organizer=Organizer(
            email="instructor@yogastudio.com",
            name="Yoga Instructor"
        ),
        recurrence=Recurrence(
            frequency=RecurrenceFrequency.WEEKLY,
            by_day=["WE", "SA"],  # Wednesday and Saturday
            until=datetime(2024, 4, 30, 23, 59, 59)  # Until end of April
        ),
        categories=["Health", "Yoga", "Fitness"],
        custom_properties={
            "X-CLASS-TYPE": "Vinyasa Flow",
            "X-LEVEL": "All Levels",
            "X-INSTRUCTOR": "Jane Yogi"
        }
    )

    # Example 4: Monthly board meetings
    print("4. Monthly board meetings...")
    monthly_builder = CalendarBuilder(
        calendar_name="Board Meetings 2024",
        timezone="America/New_York",
        template="recurring"
    )

    monthly_builder.add_event(
        summary="Board of Directors Meeting",
        start=datetime(2024, 1, 15, 10, 0, 0),  # Third Monday
        duration="PT3H",
        description="Monthly board meeting to review company performance, approve budgets, and discuss strategic initiatives",
        location="Executive Boardroom",
        organizer=Organizer(
            email="ceo@company.com",
            name="CEO"
        ),
        attendees=[
            Attendee(
                email="board.member1@company.com",
                name="Board Member 1",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="board.member2@company.com",
                name="Board Member 2",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="secretary@company.com",
                name="Corporate Secretary",
                role=AttendeeRole.OPTIONAL,
                rsvp=False
            ),
        ],
        recurrence=Recurrence(
            frequency=RecurrenceFrequency.MONTHLY,
            by_day=["MO"],  # Monday
            by_month_day=[15],  # 15th of each month (or closest Monday)
            count=12  # One year
        ),
        categories=["Executive", "Board"],
        custom_properties={
            "X-MEETING-TYPE": "Board of Directors",
            "X-QUORUM-REQUIRED": "Yes"
        }
    )

    # Example 5: Quarterly reviews
    print("5. Quarterly business reviews...")
    quarterly_builder = CalendarBuilder(
        calendar_name="Quarterly Reviews 2024",
        timezone="America/Chicago",
        template="recurring"
    )

    quarterly_builder.add_event(
        summary="Quarterly Business Review",
        start=datetime(2024, 1, 31, 9, 0, 0),
        duration="PT4H",
        description="Comprehensive review of quarterly performance: financials, KPIs, customer feedback, and strategic planning for next quarter",
        location="Main Conference Room",
        organizer=Organizer(
            email="cfo@company.com",
            name="CFO"
        ),
        attendees=[
            Attendee(
                email="ceo@company.com",
                name="CEO",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="vp.sales@company.com",
                name="VP Sales",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="vp.engineering@company.com",
                name="VP Engineering",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
            Attendee(
                email="vp.marketing@company.com",
                name="VP Marketing",
                role=AttendeeRole.REQUIRED,
                rsvp=True
            ),
        ],
        recurrence=Recurrence(
            frequency=RecurrenceFrequency.MONTHLY,
            interval=3,  # Every 3 months
            count=4  # Q1, Q2, Q3, Q4
        ),
        categories=["Executive", "Quarterly Review"],
        custom_properties={
            "X-MEETING-TYPE": "Quarterly Business Review",
            "X-PREPARATION-REQUIRED": "Yes - Submit reports 3 days prior"
        }
    )

    # Example 6: Annual events
    print("6. Annual company events...")
    annual_builder = CalendarBuilder(
        calendar_name="Annual Company Events",
        timezone="America/New_York",
        template="recurring"
    )

    annual_builder.add_event(
        summary="Annual Company Retreat",
        start=datetime(2024, 7, 15, 9, 0, 0),
        duration="P3D",  # 3 days
        description="Annual all-company retreat for team building, strategic planning, and celebration",
        location="Mountain Resort, Aspen, CO",
        organizer=Organizer(
            email="hr@company.com",
            name="HR Department"
        ),
        recurrence=Recurrence(
            frequency=RecurrenceFrequency.YEARLY,
            count=5  # Next 5 years
        ),
        categories=["Company", "Retreat", "Annual"],
        custom_properties={
            "X-EVENT-TYPE": "Company Retreat",
            "X-ATTENDANCE": "All employees"
        }
    )

    # Generate all calendars
    print("\n" + "=" * 50)
    print("Generating calendar files...")

    # Team meetings
    weekly_file = "examples/output/recurring_team_meetings.ics"
    weekly_builder.save(weekly_file)
    print(f"✓ Created: {weekly_file} ({len(weekly_builder.events)} recurring events)")

    # Yoga classes
    class_file = "examples/output/recurring_yoga_classes.ics"
    class_builder.save(class_file)
    print(f"✓ Created: {class_file} ({len(class_builder.events)} recurring classes)")

    # Board meetings
    monthly_file = "examples/output/recurring_board_meetings.ics"
    monthly_builder.save(monthly_file)
    print(f"✓ Created: {monthly_file} ({len(monthly_builder.events)} recurring meetings)")

    # Quarterly reviews
    quarterly_file = "examples/output/recurring_quarterly_reviews.ics"
    quarterly_builder.save(quarterly_file)
    print(f"✓ Created: {quarterly_file} ({len(quarterly_builder.events)} recurring reviews)")

    # Annual events
    annual_file = "examples/output/recurring_annual_events.ics"
    annual_builder.save(annual_file)
    print(f"✓ Created: {annual_file} ({len(annual_builder.events)} recurring events)")

    print("\n" + "=" * 50)
    print("Recurring template examples complete!")
    print("\nFeatures demonstrated:")
    print("  • DAILY recurrence (weekdays only with BYDAY)")
    print("  • WEEKLY recurrence (single and multiple days)")
    print("  • BIWEEKLY recurrence (interval=2)")
    print("  • MONTHLY recurrence (by day and by month day)")
    print("  • QUARTERLY recurrence (interval=3)")
    print("  • YEARLY recurrence")
    print("  • COUNT-based endings (fixed number of occurrences)")
    print("  • UNTIL-based endings (specific end date)")
    print("  • Organizers and attendees with RSVP")
    print("  • Multi-day recurring events (3-day retreat)")


if __name__ == "__main__":
    main()
