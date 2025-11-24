"""
Wikidata Linking Script - Assignment 4 & 5

Enriches local_areas-updated.csv with Wikidata information:
- Assignment 4: Fills area_name and area_code (Q-number) using coordinates
- Assignment 5: Creates local_areas-with-links.csv with owl:sameAs links

Usage:
    python scripts/linking.py
"""

import os
import socket
import time
from pathlib import Path

import certifi
import pandas as pd
from SPARQLWrapper import JSON, SPARQLExceptions, SPARQLWrapper

os.environ["SSL_CERT_FILE"] = certifi.where()

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
CSV_DIR = BASE_DIR / "csv"

DF_FINAL_INPUT = DATA_DIR / "df_final-updated.csv"
LOCAL_AREAS_INPUT = DATA_DIR / "local_areas-updated.csv"
LOCAL_AREAS_OUTPUT = DATA_DIR / "local_areas-updated.csv"
LOCAL_AREAS_WITH_LINKS_OUTPUT = DATA_DIR / "local_areas-with-links.csv"
LOCAL_AREAS_SAMPLE = CSV_DIR / "local_areas-updated.csv"
LOCAL_AREAS_WITH_LINKS_SAMPLE = CSV_DIR / "local_areas-with-links.csv"

SAMPLE_SIZE = 500

# Initialize Wikidata SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)


def get_wikidata_info(lat, lon, retries=2, timeout=15):
    """
    Query Wikidata for the nearest geographic entity to given coordinates.

    Returns:
        tuple: (area_name, area_code, wikidata_uri) or (None, None, None)
    """
    query = f"""
    SELECT ?item ?itemLabel ?distance WHERE {{
      SERVICE wikibase:around {{
        ?item wdt:P625 ?coord .
        bd:serviceParam wikibase:center "Point({lon} {lat})"^^geo:wktLiteral .
        bd:serviceParam wikibase:radius "10" .
        bd:serviceParam wikibase:distance ?distance .
      }}
      SERVICE wikibase:label {{ 
        bd:serviceParam wikibase:language "es,en" .
      }}
    }}
    ORDER BY ?distance
    LIMIT 1
    """

    sparql.setQuery(query)

    for attempt in range(retries + 1):
        try:
            sparql.setTimeout(timeout)
            results = sparql.query().convert()
            bindings = results["results"]["bindings"]

            if bindings:
                item_uri = bindings[0]["item"]["value"]
                item_label = bindings[0].get("itemLabel", {}).get("value", "")
                q_code = item_uri.split("/")[-1]
                return item_label, q_code, item_uri
            else:
                return None, None, None

        except (SPARQLExceptions.EndPointNotFound, socket.timeout):
            if attempt == retries:
                return None, None, None
            time.sleep(1)

        except Exception:
            if attempt == retries:
                return None, None, None
            time.sleep(1)

    return None, None, None


def cleanup_datasets():
    """
    Remove rows where area_name/area_code is empty AND stop_id not in df_final.
    Updates both full datasets and sample files.
    """
    # Load datasets
    df_final = pd.read_csv(DF_FINAL_INPUT, low_memory=False)
    df_areas = pd.read_csv(LOCAL_AREAS_OUTPUT)
    df_areas_with_links = pd.read_csv(LOCAL_AREAS_WITH_LINKS_OUTPUT)

    # Get valid stop_ids
    valid_stop_ids = set(df_final["stop_id"].astype(str).unique())

    # Identify rows to remove
    missing_mask = (
        df_areas["area_name"].isna()
        | (df_areas["area_name"] == "")
        | df_areas["area_code"].isna()
        | (df_areas["area_code"] == "")
    )
    invalid_stop_mask = ~df_areas["stop_id"].astype(str).isin(valid_stop_ids)
    rows_to_remove = missing_mask & invalid_stop_mask

    num_to_remove = rows_to_remove.sum()

    if num_to_remove > 0:
        # Remove rows
        df_areas_cleaned = df_areas[~rows_to_remove].copy()
        df_areas_with_links_cleaned = df_areas_with_links[~rows_to_remove].copy()

        # Save cleaned datasets
        df_areas_cleaned.to_csv(LOCAL_AREAS_OUTPUT, index=False)
        df_areas_with_links_cleaned.to_csv(LOCAL_AREAS_WITH_LINKS_OUTPUT, index=False)

        # Update sample files
        df_areas_cleaned.head(SAMPLE_SIZE).to_csv(LOCAL_AREAS_SAMPLE, index=False)
        df_areas_with_links_cleaned.head(SAMPLE_SIZE).to_csv(
            LOCAL_AREAS_WITH_LINKS_SAMPLE, index=False
        )

        return num_to_remove

    return 0


def main():
    """Main linking process for Assignment 4 & 5."""
    print("\n" + "=" * 70)
    print("WIKIDATA LINKING")
    print("=" * 70)
    print("\nThis will take approximately 1 hour to complete.")
    print("Querying Wikidata for 7,852 bus stops...")

    # Load datasets
    print("\n[1/4] Loading datasets...")
    df_final = pd.read_csv(DF_FINAL_INPUT, low_memory=False)
    df_areas = pd.read_csv(LOCAL_AREAS_INPUT)
    print(f"✓ Loaded {len(df_areas):,} stops")

    # Build coordinate lookup
    print("\n[2/4] Building coordinate lookup...")
    coord_lookup = {}
    unique_stops = df_final[["stop_id", "stop_lat", "stop_lon"]].drop_duplicates(
        subset=["stop_id"]
    )
    for _, row in unique_stops.iterrows():
        if pd.notna(row["stop_lat"]) and pd.notna(row["stop_lon"]):
            coord_lookup[str(row["stop_id"])] = (
                float(row["stop_lat"]),
                float(row["stop_lon"]),
            )
    print(f"✓ Created lookup for {len(coord_lookup):,} coordinates")

    # Query Wikidata
    print("\n[3/4] Querying Wikidata...")
    area_names = []
    area_codes = []
    wikidata_links = []

    processed = 0
    found = 0

    for idx, row in df_areas.iterrows():
        stop_id = str(row["stop_id"])

        if stop_id not in coord_lookup:
            area_names.append("")
            area_codes.append("")
            wikidata_links.append("")
            processed += 1
            continue

        lat, lon = coord_lookup[stop_id]
        area_name, area_code, wikidata_uri = get_wikidata_info(lat, lon)

        if area_name:
            area_names.append(area_name)
            area_codes.append(area_code)
            wikidata_links.append(wikidata_uri)
            found += 1
        else:
            area_names.append("")
            area_codes.append("")
            wikidata_links.append("")

        processed += 1

        # Progress update every 500 stops
        if processed % 500 == 0:
            print(
                f"  Progress: {processed}/{len(df_areas)} ({processed / len(df_areas) * 100:.1f}%)"
            )

        # Respect Wikidata usage policy
        time.sleep(0.25)

    print(f"✓ Completed {processed:,} stops ({found:,} matched)")

    # Update datasets
    print("\n[4/4] Saving datasets...")

    # Assignment 4: local_areas-updated.csv
    df_areas["area_name"] = area_names
    df_areas["area_code"] = area_codes
    df_areas.to_csv(LOCAL_AREAS_OUTPUT, index=False)

    # Assignment 5: local_areas-with-links.csv
    df_areas_with_links = df_areas.copy()
    df_areas_with_links["wikidata_link"] = wikidata_links
    df_areas_with_links.to_csv(LOCAL_AREAS_WITH_LINKS_OUTPUT, index=False)

    # Create samples
    df_areas.head(SAMPLE_SIZE).to_csv(LOCAL_AREAS_SAMPLE, index=False)
    df_areas_with_links.head(SAMPLE_SIZE).to_csv(
        LOCAL_AREAS_WITH_LINKS_SAMPLE, index=False
    )

    print("✓ Saved full datasets and samples")

    # Cleanup invalid rows
    print("\n[5/5] Cleaning up invalid rows...")
    removed = cleanup_datasets()
    if removed > 0:
        print(f"✓ Removed {removed:,} invalid rows")
    else:
        print("✓ No invalid rows found")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total processed: {processed:,}")
    print(f"Wikidata matched: {found:,} ({found / processed * 100:.1f}%)")
    print(f"\nFiles created:")
    print(f"  - local_areas-updated.csv (Assignment 4)")
    print(f"  - local_areas-with-links.csv (Assignment 5)")
    print("\n✓ Ready for RDF transformation")
    print("=" * 70)


if __name__ == "__main__":
    main()
