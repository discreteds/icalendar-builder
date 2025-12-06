#!/usr/bin/env python3
"""
Example: Music Template
========================

Demonstrates the music template for concerts, festivals, and music events.
This template automatically:
- Adds "Music,Concert" categories
- Includes a default 15-minute reminder alarm
- Optimizes for artist, venue, and ticketing information
"""

from datetime import datetime
from icalendar_builder import CalendarBuilder
from icalendar_builder.models import Alarm, AlarmAction


def main():
    """Create music calendars for concerts, festivals, and gigs."""
    print("Music Template Example")
    print("=" * 50)

    # Example 1: Concert tour calendar
    print("\n1. Creating concert tour calendar...")
    tour_builder = CalendarBuilder(
        calendar_name="Taylor Swift - The Eras Tour 2024",
        timezone="America/New_York",
        template="music"
    )

    # Multiple tour dates
    tour_dates = [
        ("Miami, FL", "Hard Rock Stadium", datetime(2024, 10, 18, 19, 0, 0)),
        ("New Orleans, LA", "Caesars Superdome", datetime(2024, 10, 25, 19, 0, 0)),
        ("Indianapolis, IN", "Lucas Oil Stadium", datetime(2024, 11, 1, 19, 0, 0)),
    ]

    for city, venue, start_time in tour_dates:
        tour_builder.add_event(
            summary=f"Taylor Swift - {city}",
            start=start_time,
            duration="PT3H",
            description="The Eras Tour - A journey through Taylor Swift's musical eras",
            location=f"{venue}, {city}",
            url="https://www.ticketmaster.com/taylor-swift",
            categories=["Concert", "Pop"],
            custom_properties={
                "X-ARTIST": "Taylor Swift",
                "X-TOUR": "The Eras Tour",
                "X-VENUE": venue,
                "X-GENRE": "Pop",
                "X-TICKET-PRICE": "$49.50 - $449.50"
            }
        )

    # Example 2: Music festival
    print("2. Creating music festival calendar...")
    festival_builder = CalendarBuilder(
        calendar_name="Coachella 2024",
        timezone="America/Los_Angeles",
        template="music"
    )

    # Festival days with multiple sets
    festival_schedule = [
        # Weekend 1 - Day 1
        {
            "summary": "Coachella Day 1 - Headliner: Lana Del Rey",
            "start": datetime(2024, 4, 12, 11, 0, 0),
            "end": datetime(2024, 4, 13, 1, 0, 0),
            "artists": ["Lana Del Rey", "Tyler, The Creator", "Doja Cat"],
        },
        # Weekend 1 - Day 2
        {
            "summary": "Coachella Day 2 - Headliner: Tyler, The Creator",
            "start": datetime(2024, 4, 13, 11, 0, 0),
            "end": datetime(2024, 4, 14, 1, 0, 0),
            "artists": ["Tyler, The Creator", "Bjork", "Blur"],
        },
        # Weekend 1 - Day 3
        {
            "summary": "Coachella Day 3 - Headliner: Frank Ocean",
            "start": datetime(2024, 4, 14, 11, 0, 0),
            "end": datetime(2024, 4, 15, 1, 0, 0),
            "artists": ["Frank Ocean", "Calvin Harris", "Gorillaz"],
        },
    ]

    for day in festival_schedule:
        lineup = ", ".join(day["artists"])
        festival_builder.add_event(
            summary=day["summary"],
            start=day["start"],
            end=day["end"],
            description=f"Lineup includes: {lineup}",
            location="Empire Polo Club, Indio, CA",
            url="https://www.coachella.com",
            categories=["Festival", "Music", "Multi-Genre"],
            custom_properties={
                "X-FESTIVAL": "Coachella Valley Music and Arts Festival",
                "X-LINEUP": lineup,
                "X-CAPACITY": "125000"
            },
            # Custom alarm for festival (earlier warning)
            alarms=[
                Alarm(
                    action=AlarmAction.DISPLAY,
                    trigger="-PT2H",
                    description="Festival starts in 2 hours - plan your travel!"
                ),
            ]
        )

    # Example 3: Local venue gig calendar
    print("3. Creating local venue calendar...")
    venue_builder = CalendarBuilder(
        calendar_name="The Troubadour - October 2024",
        timezone="America/Los_Angeles",
        template="music"
    )

    # Weekly shows at a venue
    shows = [
        {
            "artist": "Japanese Breakfast",
            "date": datetime(2024, 10, 5, 20, 0, 0),
            "genre": "Indie Rock",
            "opener": "Vagabon",
        },
        {
            "artist": "Phoebe Bridgers",
            "date": datetime(2024, 10, 12, 20, 0, 0),
            "genre": "Indie Folk",
            "opener": "MUNA",
        },
        {
            "artist": "Boy Genius",
            "date": datetime(2024, 10, 19, 20, 0, 0),
            "genre": "Indie Folk",
            "opener": "MUNA",
        },
        {
            "artist": "Mitski",
            "date": datetime(2024, 10, 26, 20, 0, 0),
            "genre": "Indie Rock",
            "opener": "Jay Som",
        },
    ]

    for show in shows:
        description = f"Doors at 7:00 PM, Show at 8:00 PM"
        if show["opener"]:
            description += f"\nOpening act: {show['opener']}"

        venue_builder.add_event(
            summary=f"{show['artist']} at The Troubadour",
            start=show["date"],
            duration="PT3H",
            description=description,
            location="The Troubadour, West Hollywood, CA",
            url="https://www.troubadour.com",
            categories=["Concert", show["genre"], "Indie"],
            custom_properties={
                "X-ARTIST": show["artist"],
                "X-VENUE": "The Troubadour",
                "X-GENRE": show["genre"],
                "X-OPENING-ACT": show.get("opener", "TBA"),
                "X-DOORS": "19:00",
                "X-AGE-RESTRICTION": "21+"
            }
        )

    # Example 4: Opera performance
    print("4. Creating opera calendar...")
    opera_builder = CalendarBuilder(
        calendar_name="Metropolitan Opera - Winter Season",
        timezone="America/New_York",
        template="music"
    )

    opera_builder.add_event(
        summary="La Bohème by Giacomo Puccini",
        start=datetime(2024, 12, 15, 19, 30, 0),
        duration="PT3H30M",  # Including intermissions
        description="Puccini's timeless tale of love and loss in 1830s Paris. "
                    "Sung in Italian with English subtitles. Two 15-minute intermissions.",
        location="Metropolitan Opera House, Lincoln Center, New York, NY",
        url="https://www.metopera.org",
        categories=["Opera", "Classical"],
        custom_properties={
            "X-COMPOSER": "Giacomo Puccini",
            "X-CONDUCTOR": "Yannick Nézet-Séguin",
            "X-DIRECTOR": "Franco Zeffirelli",
            "X-LANGUAGE": "Italian",
            "X-SUBTITLES": "English",
            "X-DURATION": "3 hours 30 minutes (including intermissions)"
        },
        # Opera needs earlier arrival time
        alarms=[
            Alarm(
                action=AlarmAction.DISPLAY,
                trigger="-PT45M",
                description="Opera starts in 45 minutes - arrive early for seating"
            ),
        ]
    )

    # Generate all calendars
    print("\n" + "=" * 50)
    print("Generating calendar files...")

    # Concert tour
    tour_file = "examples/output/music_eras_tour.ics"
    tour_builder.save(tour_file)
    print(f"✓ Created: {tour_file} ({len(tour_builder.events)} shows)")

    # Festival
    festival_file = "examples/output/music_coachella.ics"
    festival_builder.save(festival_file)
    print(f"✓ Created: {festival_file} ({len(festival_builder.events)} days)")

    # Venue shows
    venue_file = "examples/output/music_troubadour.ics"
    venue_builder.save(venue_file)
    print(f"✓ Created: {venue_file} ({len(venue_builder.events)} shows)")

    # Opera
    opera_file = "examples/output/music_opera.ics"
    opera_builder.save(opera_file)
    print(f"✓ Created: {opera_file} ({len(opera_builder.events)} performances)")

    print("\n" + "=" * 50)
    print("Music template examples complete!")
    print("\nFeatures demonstrated:")
    print("  • Automatic 'Music,Concert' categories")
    print("  • Default 15-minute reminder alarm")
    print("  • Custom alarms for festivals (2 hours) and opera (45 minutes)")
    print("  • Artist and venue information")
    print("  • Tour schedules")
    print("  • Multi-day festival events")
    print("  • Genre classification")
    print("  • Ticket and age restriction info")
    print("  • Various music types: Pop, Indie, Opera")


if __name__ == "__main__":
    main()
