"""
GTFS Madrid Dataset - Data Cleaning for RDF Transformation

Prepares CSV files for RDF transformation by:
1. Removing auto-increment indices
2. Trimming all string columns
3. Converting dates to ISO 8601 format (YYYYMMDD → YYYY-MM-DD)
4. Creating local_areas.csv placeholder

Outputs:
- Full datasets in data/processed/ with -updated.csv suffix
- 500-row samples in csv/ for repository
"""

from pathlib import Path

import pandas as pd


def remove_auto_increment_index(df):
    """Remove auto-increment index column if present."""
    if len(df.columns) > 0:
        first_col = df.columns[0]
        if (
            first_col == ""
            or "Unnamed" in str(first_col)
            or (df[first_col].equals(pd.Series(range(len(df)))))
        ):
            return df.iloc[:, 1:]
    return df


def trim_string_columns(df):
    """Trim whitespace from all string columns."""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()
    return df


def convert_gtfs_date_to_iso(date_series):
    """Convert GTFS date format (YYYYMMDD) to ISO 8601 (YYYY-MM-DD)."""
    return pd.to_datetime(date_series, format="%Y%m%d").dt.strftime("%Y-%m-%d")


def process_merged_dataset(input_dir, output_dir):
    """Process the main merged GTFS dataset."""
    df = pd.read_csv(input_dir / "df_final.csv", low_memory=False)

    # Remove auto-increment index if present
    df = remove_auto_increment_index(df)

    # Trim all string columns
    df = trim_string_columns(df)

    # Save
    output_file = output_dir / "df_final-updated.csv"
    df.to_csv(output_file, index=False)

    return df


def process_calendar(input_dir, output_dir):
    """Process calendar.csv - convert dates to ISO 8601."""
    df = pd.read_csv(input_dir / "calendar.csv")

    # Trim strings
    df = trim_string_columns(df)

    # Convert dates to ISO 8601
    df["start_date"] = convert_gtfs_date_to_iso(df["start_date"])
    df["end_date"] = convert_gtfs_date_to_iso(df["end_date"])

    # Save
    df.to_csv(output_dir / "calendar-updated.csv", index=False)
    return df


def process_calendar_dates(input_dir, output_dir):
    """Process calendar_dates.csv - convert dates to ISO 8601."""
    df = pd.read_csv(input_dir / "calendar_dates.csv")

    # Trim strings
    df = trim_string_columns(df)

    # Convert dates to ISO 8601
    df["date"] = convert_gtfs_date_to_iso(df["date"])

    # Save
    df.to_csv(output_dir / "calendar_dates-updated.csv", index=False)
    return df


def process_shapes(input_dir, output_dir):
    """Process shapes.csv."""
    df = pd.read_csv(input_dir / "shapes.csv")

    # Trim strings
    df = trim_string_columns(df)

    # Save
    df.to_csv(output_dir / "shapes-updated.csv", index=False)
    return df


def create_local_areas_template(input_dir, output_dir):
    """
    Create local_areas-updated.csv with placeholder columns.
    Will be filled by linking.py with Wikidata information.
    """
    stops_df = pd.read_csv(input_dir / "stops.csv", usecols=["stop_id"])
    unique_stop_ids = (
        stops_df["stop_id"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    df_areas = pd.DataFrame(
        {
            "stop_id": unique_stop_ids,
            "area_name": ["" for _ in unique_stop_ids],
            "area_code": ["" for _ in unique_stop_ids],
        }
    )

    df_areas.to_csv(output_dir / "local_areas-updated.csv", index=False)
    return df_areas


def create_sample_files(output_dir, csv_dir):
    """Create 500-row sample files for repository."""
    csv_dir.mkdir(exist_ok=True)

    files_to_sample = [
        "df_final-updated.csv",
        "calendar-updated.csv",
        "calendar_dates-updated.csv",
        "shapes-updated.csv",
        "local_areas-updated.csv",
    ]

    for filename in files_to_sample:
        input_file = output_dir / filename
        if input_file.exists():
            df = pd.read_csv(input_file)
            df.head(500).to_csv(csv_dir / filename, index=False)


def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("DATA CLEANING & PREPARATION")
    print("=" * 70)

    # Setup paths
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / "data/processed"
    output_dir = base_dir / "data/processed"
    csv_dir = base_dir / "csv"

    # Process all datasets
    print("\n[1/6] Processing df_final.csv...")
    df_merged = process_merged_dataset(input_dir, output_dir)
    print(f"✓ Cleaned {len(df_merged):,} rows")

    print("\n[2/6] Processing calendar.csv...")
    df_calendar = process_calendar(input_dir, output_dir)
    print(f"✓ Converted dates: {len(df_calendar):,} rows")

    print("\n[3/6] Processing calendar_dates.csv...")
    df_calendar_dates = process_calendar_dates(input_dir, output_dir)
    print(f"✓ Converted dates: {len(df_calendar_dates):,} rows")

    print("\n[4/6] Processing shapes.csv...")
    df_shapes = process_shapes(input_dir, output_dir)
    print(f"✓ Cleaned {len(df_shapes):,} rows")

    print("\n[5/6] Creating local_areas placeholder...")
    df_areas = create_local_areas_template(input_dir, output_dir)
    print(f"✓ Created {len(df_areas):,} placeholders")

    print("\n[6/6] Creating 500-row samples...")
    create_sample_files(output_dir, csv_dir)
    print("✓ Created sample files in csv/")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Routes:       {df_merged['route_id'].nunique():>10,}")
    print(f"Stops:        {df_merged['stop_id'].nunique():>10,}")
    print(f"Trips:        {df_merged['trip_id'].nunique():>10,}")
    print(f"Stop-times:   {len(df_merged):>10,}")
    print(f"Services:     {df_merged['service_id'].nunique():>10,}")
    print("\n✓ Ready for linking.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
