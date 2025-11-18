"""
GTFS Madrid Dataset Preprocessing Script

Prepares the Madrid CRTM GTFS dataset for RDF transformation:
1. Converts .txt files to .csv
2. Normalizes GTFS extended times (e.g., 24:05:00 → 00:05:00)
3. Creates merged dataset with service_id for schedule filtering
4. Processes calendar data for date filtering

Output: data/processed/ directory with clean CSV files
"""

from pathlib import Path

import pandas as pd


def normalize_gtfs_time(value):
    """Ensure GTFS extended times (>=24h) wrap into a single-day clock."""
    if pd.isna(value):
        return value

    text = str(value).strip()
    if not text:
        return text

    parts = text.split(":")
    if len(parts) < 2:
        return text

    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) > 2 else 0
    except ValueError:
        return text

    if hours < 24:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    normalized_hours = hours % 24
    return f"{normalized_hours:02d}:{minutes:02d}:{seconds:02d}"


def normalize_time_columns(df, columns):
    """Normalize GTFS time columns and return change counts."""
    stats = {}
    for column in columns:
        original = df[column].copy()
        normalized = df[column].apply(normalize_gtfs_time)
        changes = (original.fillna("__nan__") != normalized.fillna("__nan__")).sum()
        df[column] = normalized
        stats[column] = int(changes)
    return stats


def convert_txt_to_csv(source_dir, output_dir, gtfs_files):
    """Convert GTFS .txt files to .csv format."""
    output_dir.mkdir(exist_ok=True)
    stats = {}

    for file_name in gtfs_files:
        source_file = source_dir / f"{file_name}.txt"
        output_file = output_dir / f"{file_name}.csv"

        try:
            df = pd.read_csv(source_file)
            df.to_csv(output_file, index=False)
            stats[file_name] = {"records": len(df), "columns": len(df.columns)}
        except Exception as e:
            stats[file_name] = {"records": 0, "columns": 0, "error": str(e)}

    return stats


def verify_data_integrity(output_dir):
    """Verify referential integrity of GTFS data and normalize times."""
    routes = pd.read_csv(output_dir / "routes.csv")
    trips = pd.read_csv(output_dir / "trips.csv")
    stops = pd.read_csv(output_dir / "stops.csv")
    stop_times = pd.read_csv(output_dir / "stop_times.csv")

    # Check referential integrity
    trips_valid = trips["route_id"].isin(routes["route_id"]).sum()
    stop_times_trips_valid = stop_times["trip_id"].isin(trips["trip_id"]).sum()
    stop_times_stops_valid = stop_times["stop_id"].isin(stops["stop_id"]).sum()

    all_valid = (
        trips_valid == len(trips)
        and stop_times_trips_valid == len(stop_times)
        and stop_times_stops_valid == len(stop_times)
    )

    if not all_valid:
        print("⚠️  WARNING: Integrity issues detected")

    # Normalize times
    time_fix_stats = normalize_time_columns(
        stop_times, ["arrival_time", "departure_time"]
    )

    return routes, trips, stops, stop_times, time_fix_stats


def create_merged_dataset(routes, trips, stops, stop_times, output_dir):
    """Create merged dataset: routes → trips → stop_times → stops."""
    # Merge all tables
    df = trips.merge(routes, on="route_id", how="left")
    df = df.merge(stop_times, on="trip_id", how="left")
    df = df.merge(stops, on="stop_id", how="left")

    # Keep essential columns
    essential_cols = [
        "trip_id",
        "route_id",
        "service_id",
        "trip_headsign",
        "direction_id",
        "shape_id",
        "route_short_name",
        "route_long_name",
        "route_type",
        "stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon",
        "arrival_time",
        "departure_time",
        "stop_sequence",
        "wheelchair_boarding",
    ]

    available_cols = [col for col in essential_cols if col in df.columns]
    df_final = df[available_cols].copy()

    # Save
    output_file = output_dir / "df_final.csv"
    df_final.to_csv(output_file, index=False)

    return df_final


def process_calendar_data(output_dir):
    """Load and verify calendar data."""
    calendar = pd.read_csv(output_dir / "calendar.csv")
    calendar_dates = pd.read_csv(output_dir / "calendar_dates.csv")
    return calendar, calendar_dates


def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("GTFS PREPROCESSING")
    print("=" * 70)

    # Setup paths
    base_dir = Path(__file__).parent.parent
    source_dir = base_dir / "data/raw"
    output_dir = base_dir / "data/processed"

    # GTFS files to process
    gtfs_files = [
        "agency",
        "routes",
        "trips",
        "stops",
        "stop_times",
        "calendar",
        "calendar_dates",
        "shapes",
    ]

    # Step 1: Convert .txt to .csv
    print("\n[1/4] Converting .txt to .csv...")
    stats = convert_txt_to_csv(source_dir, output_dir, gtfs_files)
    print(f"✓ Converted {len([s for s in stats.values() if 'error' not in s])} files")

    # Step 2: Verify integrity and normalize times
    print("\n[2/4] Verifying data integrity...")
    routes, trips, stops, stop_times, time_fix_stats = verify_data_integrity(output_dir)
    print("✓ Integrity check complete")

    total_fixes = sum(time_fix_stats.values())
    if total_fixes:
        print(f"✓ Normalized {total_fixes:,} extended-time values")

    # Step 3: Create merged dataset
    print("\n[3/4] Creating merged dataset...")
    df_final = create_merged_dataset(routes, trips, stops, stop_times, output_dir)
    print(f"✓ Created df_final.csv: {len(df_final):,} rows")

    # Step 4: Process calendar data
    print("\n[4/4] Processing calendar data...")
    calendar, calendar_dates = process_calendar_data(output_dir)
    print(
        f"✓ Loaded calendar data: {len(calendar):,} rules, {len(calendar_dates):,} exceptions"
    )

    # Summary
    shapes = pd.read_csv(output_dir / "shapes.csv")
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Routes:       {df_final['route_id'].nunique():>10,}")
    print(f"Trips:        {df_final['trip_id'].nunique():>10,}")
    print(f"Stops:        {df_final['stop_id'].nunique():>10,}")
    print(f"Stop-times:   {len(df_final):>10,}")
    print(f"Services:     {df_final['service_id'].nunique():>10,}")
    print(f"Shape points: {len(shapes):>10,}")
    print("\n✓ Ready for assignment3.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
