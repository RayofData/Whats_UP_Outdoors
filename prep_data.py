"""Run the offline DNR trail preparation pipeline."""

import json
from pathlib import Path

import geopandas as gpd 

from src.apis.dnr_api import (
    build_profile,
    download_all_features,
    get_object_ids,
    validate_download,
)

from src.trails import (
    group_trails,
    prep_columns,
    replace_missing_placeholders,
    add_length_category
)


RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")

OUTPUT_PATH = RAW_DIR / "dnr_up_hiking_trails.geojson"
PROFILE_PATH = REPORT_DIR / "dnr_up_hiking_trails_profile.json"

PROCESSED_DIR = Path("data/processed")

PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"



def main():
    try:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(
            f"Could not create output directories: {exc}"
        ) from exc

    print("Requesting all matching object IDs...")
    object_ids = get_object_ids()

    feature_collection = download_all_features(object_ids)

    try: 
        OUTPUT_PATH.write_text(
            json.dumps(feature_collection),
            encoding="utf-8"
        )
    except OSError as exc:
        raise RuntimeError(
            f"Could not save raw GeoJSON to {OUTPUT_PATH}: {exc}"
        ) from exc

    print("\nLoading combined GeoJSON with GeoPandas...")

    try:
        trails = gpd.read_file(OUTPUT_PATH)
    except OSError as exc:
        raise RuntimeError(
            f"Could not read raw GeoJSON from {OUTPUT_PATH}: {exc}"
        ) from exc

    validate_download(trails, object_ids)

    profile = build_profile(
        trails = trails, 
        expected_count=len(object_ids),
    )

    try: 
        PROFILE_PATH.write_text(
            json.dumps(profile, indent=2, default=str),
            encoding="utf-8"
        )
    except OSError as exc:
        raise RuntimeError(
            f"Could not save profile to {PROFILE_PATH}: {exc}"
        ) from exc

    print("\nFull download complete.")
    print(f"Downloaded records: {len(trails):,}")
    print(f"CRS: {trails.crs}")
    print("Geometry types:\n" f"{trails.geometry.geom_type.value_counts()}")
    print(f"GeoJSON saved to: {OUTPUT_PATH}")
    print(f"Profile saved to: {PROFILE_PATH}")

    cleaned_trails = replace_missing_placeholders(trails)   
    prepared_trails = prep_columns(cleaned_trails)
    grouped_trails = group_trails(prepared_trails)
    final_trails = add_length_category(grouped_trails)

    final_trails = final_trails[
    [
        "TrailGroupName",
        "HikingName",
        "County",
        "LengthCategory",
        "ReportedLengthMiles",
        "TrailWidth",
        "SurfaceTypes",
        "AccessibilityValues",
        "TrailStatuses",
        "FacilityName",
        "SegmentCount",
        "geometry",
    ]
]

    try: 
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(
            f"Could not create output directories: {exc}"
        ) from exc

    try:
        final_trails.to_parquet(PROCESSED_PATH, index=False)
    except OSError as exc:
        raise RuntimeError(
            f"Could not save processed trails to {PROCESSED_PATH}: {exc}"
        ) from exc

    print(f"\nProcessed data saved to : {PROCESSED_PATH}")
    print("Processed trail data:")
    print(f"Grouped trails: {len(final_trails):,}")
    print(f"CRS: {final_trails.crs}")
    print(f"Columns: {list(final_trails.columns)}")

    print("\nLength categories: ")
    print(final_trails["LengthCategory"].value_counts(dropna=False))

    print("\nSample trails:")
    print(
        final_trails[
            [
                "TrailGroupName",
                "ReportedLengthMiles",
                "LengthCategory",
                "TrailWidth",
                "SurfaceTypes",
                "AccessibilityValues",
                "TrailStatuses"
            ]
        ]
    .head()
    .to_string(index=False)
)



if __name__ == "__main__":
    main()