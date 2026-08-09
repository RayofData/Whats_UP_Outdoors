import json
from pathlib import Path

import geopandas as gpd 

from src.trails import (
    build_profile,
    download_all_features,
    get_object_ids,
    validate_download,
)


RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")

OUTPUT_PATH = RAW_DIR / "dnr_up_hiking_trails.geojson"
PROFILE_PATH = REPORT_DIR / "dnr_up_hiking_trails_profile.json"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Requesting all matching object IDs...")
    object_ids = get_object_ids()

    feature_collection = download_all_features(object_ids)

    OUTPUT_PATH.write_text(
        json.dumps(feature_collection),
        encoding="utf-8"
    )

    print("\nLoading combined GeoJSON with GeoPandas...")
    trails = gpd.read_file(OUTPUT_PATH)

    validate_download(trails, object_ids)

    profile = build_profile(
        trails = trails, 
        expected_count=len(object_ids),
    )

    PROFILE_PATH.write_text(
        json.dumps(profile, indent=2, default=str),
        encoding="utf-8"
    )

    print("\nFull download complete.")
    print(f"Downloaded records: {len(trails):,}")
    print(f"CRS: {trails.crs}")
    print("Geometry types:\n" f"{trails.geometry.geom_type.value_counts()}")
    print(f"GeoJSON saved to: {OUTPUT_PATH}")
    print(f"Profile saved to: {PROFILE_PATH}")

if __name__ == "__main__":
    main()