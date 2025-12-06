#!/usr/bin/env python3
"""
Example: Sport Template
========================

Demonstrates the sport template for sporting events, competitions, and matches.
This template automatically adds "Sports" category and is optimized for
sporting event information with custom properties for scores, teams, venues, etc.
"""

from datetime import datetime
from icalendar_builder import CalendarBuilder


def main():
    """Create a sports calendar for various sporting events."""
    print("Sport Template Example")
    print("=" * 50)

    # Create calendar for NBA season
    builder = CalendarBuilder(
        calendar_name="NBA 2024 Season - Lakers",
        timezone="America/Los_Angeles",
        template="sport"
    )

    # Example 1: Regular season game
    print("\n1. Regular season basketball game...")
    builder.add_event(
        summary="Lakers vs Celtics",
        start=datetime(2024, 2, 1, 19, 30, 0),
        end=datetime(2024, 2, 1, 22, 0, 0),
        description="NBA Regular Season matchup - Lakers home game",
        location="Crypto.com Arena, Los Angeles, CA",
        url="https://www.nba.com/lakers/tickets",
        categories=["Basketball", "NBA", "Home Game"],
        custom_properties={
            "X-HOME-TEAM": "Los Angeles Lakers",
            "X-AWAY-TEAM": "Boston Celtics",
            "X-VENUE": "Crypto.com Arena",
            "X-GAME-TYPE": "Regular Season",
            "X-BROADCAST": "ESPN"
        }
    )

    # Example 2: Away game
    print("2. Away game...")
    builder.add_event(
        summary="Warriors vs Lakers",
        start=datetime(2024, 2, 8, 20, 0, 0),
        duration="PT2H30M",
        description="Lakers away game at Golden State",
        location="Chase Center, San Francisco, CA",
        url="https://www.nba.com/lakers/schedule",
        categories=["Basketball", "NBA", "Away Game"],
        custom_properties={
            "X-HOME-TEAM": "Golden State Warriors",
            "X-AWAY-TEAM": "Los Angeles Lakers",
            "X-VENUE": "Chase Center",
            "X-GAME-TYPE": "Regular Season",
            "X-BROADCAST": "TNT"
        }
    )

    # Create another calendar for soccer
    print("\n3. Creating Premier League calendar...")
    soccer_builder = CalendarBuilder(
        calendar_name="Premier League 2024",
        timezone="Europe/London",
        template="sport"
    )

    # Example 3: Soccer match
    soccer_builder.add_event(
        summary="Arsenal vs Manchester United",
        start=datetime(2024, 2, 10, 15, 0, 0),
        end=datetime(2024, 2, 10, 17, 0, 0),
        description="Premier League - Matchday 25",
        location="Emirates Stadium, London",
        url="https://www.premierleague.com",
        categories=["Football", "Premier League"],
        custom_properties={
            "X-HOME-TEAM": "Arsenal",
            "X-AWAY-TEAM": "Manchester United",
            "X-COMPETITION": "Premier League",
            "X-MATCHDAY": "25",
            "X-REFEREE": "TBD"
        }
    )

    # Example 4: Tennis tournament
    print("4. Creating tennis tournament schedule...")
    tennis_builder = CalendarBuilder(
        calendar_name="Australian Open 2024",
        timezone="Australia/Melbourne",
        template="sport"
    )

    # Multiple rounds
    rounds = [
        ("Round 1", datetime(2024, 1, 14, 11, 0, 0)),
        ("Round 2", datetime(2024, 1, 17, 11, 0, 0)),
        ("Round 3", datetime(2024, 1, 19, 11, 0, 0)),
        ("Round 4", datetime(2024, 1, 21, 11, 0, 0)),
        ("Quarterfinals", datetime(2024, 1, 23, 11, 0, 0)),
        ("Semifinals", datetime(2024, 1, 25, 14, 0, 0)),
        ("Final", datetime(2024, 1, 28, 19, 30, 0)),
    ]

    for round_name, start_time in rounds:
        tennis_builder.add_event(
            summary=f"Australian Open - {round_name}",
            start=start_time,
            duration="PT4H",  # Approximate
            description=f"Men's Singles {round_name}",
            location="Melbourne Park, Melbourne",
            url="https://ausopen.com",
            categories=["Tennis", "Grand Slam"],
            custom_properties={
                "X-TOURNAMENT": "Australian Open",
                "X-ROUND": round_name,
                "X-SURFACE": "Hard Court",
                "X-CATEGORY": "Grand Slam"
            }
        )

    # Example 5: Marathon event
    print("5. Creating marathon event...")
    marathon_builder = CalendarBuilder(
        calendar_name="Running Events 2024",
        timezone="America/New_York",
        template="sport"
    )

    marathon_builder.add_event(
        summary="New York City Marathon 2024",
        start=datetime(2024, 11, 3, 8, 0, 0),
        end=datetime(2024, 11, 3, 17, 0, 0),
        description="The world's largest marathon - 50,000+ runners through all five boroughs",
        location="New York City, NY",
        url="https://www.tcsnycmarathon.org",
        categories=["Running", "Marathon"],
        custom_properties={
            "X-DISTANCE": "42.195 km",
            "X-EVENT-TYPE": "Marathon",
            "X-PARTICIPANTS": "50000+",
            "X-START-LOCATION": "Staten Island",
            "X-FINISH-LOCATION": "Central Park"
        }
    )

    # Generate all calendars
    print("\n" + "=" * 50)
    print("Generating calendar files...")

    # Basketball
    nba_file = "examples/output/sport_nba_lakers.ics"
    builder.save(nba_file)
    print(f"✓ Created: {nba_file} ({len(builder.events)} games)")

    # Soccer
    soccer_file = "examples/output/sport_premier_league.ics"
    soccer_builder.save(soccer_file)
    print(f"✓ Created: {soccer_file} ({len(soccer_builder.events)} matches)")

    # Tennis
    tennis_file = "examples/output/sport_australian_open.ics"
    tennis_builder.save(tennis_file)
    print(f"✓ Created: {tennis_file} ({len(tennis_builder.events)} rounds)")

    # Marathon
    marathon_file = "examples/output/sport_marathon.ics"
    marathon_builder.save(marathon_file)
    print(f"✓ Created: {marathon_file} ({len(marathon_builder.events)} events)")

    print("\n" + "=" * 50)
    print("Sport template examples complete!")
    print("\nFeatures demonstrated:")
    print("  • Automatic 'Sports' category")
    print("  • Team information (home/away)")
    print("  • Venue details")
    print("  • Competition types (NBA, Premier League, Grand Slam)")
    print("  • Broadcasting information")
    print("  • Event-specific metadata (rounds, distances, participants)")
    print("  • Multiple sports: Basketball, Soccer, Tennis, Running")


if __name__ == "__main__":
    main()
