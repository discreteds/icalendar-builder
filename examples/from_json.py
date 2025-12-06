"""Example of loading calendar from JSON file."""

from icalendar_builder import CalendarBuilder

print("Loading calendar from JSON file...")
print("-" * 50)

# Load and generate
builder = CalendarBuilder.from_json("examples/events/tour_de_france.json")

print(f"Calendar: {builder.calendar_name}")
print(f"Timezone: {builder.timezone}")
print(f"Events: {len(builder)}")
print()

# Save as combined calendar
output_file = builder.save("examples/output/tour_de_france_2024.ics")
print(f"✓ Created: {output_file}")

# Also save as individual files
individual_files = builder.save_individual_events(
    output_dir="examples/output/tdf_stages",
    filename_template="stage_{index}.ics"
)

print(f"✓ Created {len(individual_files)} individual stage files")
print()
print("Done! Check examples/output/ for generated files")
