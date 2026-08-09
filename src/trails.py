import json
from pathlib import Path

import geopandas as gpd 
import requests

LAYER_URL = (
    "https://gisagodnr.state.mi.us/arcgis/rest/services/"
    "DNR/DNRTrailsOPENDATA/MapServer/2"
)

QUERY_URL = f"{LAYER_URL}/query"

WHERE_CLAUSE = "Peninsula = 'Upper Peninsula'"
BATCH_SIZE = 500

RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")

OUTPUT_PATH = RAW_DIR / "dnr_up_hiking_trails.geojson"
PROFILE_PATH = REPORT_DIR / "dnr_up_hiking_trails_profile.json"

DOWNLOAD_FIELDS = [
    "OBJECTID",
    "DNRTrail",
    "TrailNamePrimary",
    "HikingName",
    "FacilityName",
    "County",
    "Peninsula",
    "Hiking",
    "TrailApprovalStatus",
    "TrailUseCategory",
    "OpenClosedStatusNonmotor",
    "SurfaceType",
    "TrailWidthFeet",
    "ADAAccessible",
    "SegmentLengthMiles",
    "SpecialRestrictionType"
]

def request_json(params):
    """Request JSON from the ArcGIS service and validate the response."""

    try: 
        response = requests.get(
            QUERY_URL,
            params=params,
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"DNR API request failed: {exc}") from exc

    try:
        payload = response.json()
    except requests.JSONDecodeError as exc:
        raise RuntimeError("DNR API did not return valid JSON.") from exc 
        
    if "error" in payload:
        error = payload["error"]
        message = error.get("message", "Unknown ArcGIS error")
        details = error.get("details", [])
        raise RuntimeError(f"{message}: {details}")

    return payload

def get_object_ids():
    """Return all object IDs matching the UP filter."""

    payload = request_json(
        {
            "where": WHERE_CLAUSE,
            "returnIdsOnly": "true",
            "returnGeometry": "false",
            "f": "json",
        }
    )

    object_ids = payload.get("objectIds")

    if object_ids is None:
        raise RuntimeError(
            "The API response did not contain an objectIds field."
        )

    if not object_ids:
        raise RuntimeError(
            "The API returned zero matching trail segments."
        )

    return sorted(int(object_id) for object_id in object_ids)


def batched(values, batch_size):
    """Yield consecutive batches from a sequence."""

    if type(batch_size) != int:
        raise ValueError("batch_size must be an integer")

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    for start in range(0, len(values), batch_size):
        yield list(values[start : start + batch_size])

def download_batch(object_ids):
    """Download one batch of features as GeoJSON."""

    payload = request_json(
        {
            "objectIds": ",".join(map(str, object_ids)),
            "outFields": ",".join(DOWNLOAD_FIELDS),
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson"
        }
    )

    features = payload.get("features")

    if features is None:
        raise RuntimeError("GeoJSON response did not contain a feature field")

    return payload


def download_all_features(object_ids):
    """Download and combine every matching trail feature."""

    combined_features = []
    batches = list(batched(object_ids, BATCH_SIZE))

    print(f"Matching object IDs: {len(object_ids):,}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Number of batches: {len(batches)}")

    for batch_number, object_id_batch in enumerate(batches, start=1):
        print(
            f"Downloading batch {batch_number}/{len(batches)} "
            f"({len(object_id_batch)} records...)"
        )

        payload = download_batch(object_id_batch)
        features = payload["features"]

        combined_features.extend(features)

    return {
        "type": "FeatureCollection",
        "features": combined_features,
    }

def build_profile(trails, expected_count):
    """Create a validation and data-quality report."""

    missing_values = []

    for column in trails.columns:
        if column != trails.geometry.name:
            missing_values[column] = int(trails[column].isna().sum())

    geometry_types = {}

    for geometry_type, count in trails.geometry.geom_type.value_counts(dropna=False).items():
        geometry_types[str(geometry_type)] = int(count)

    non_missing_geometry = trails.geometry.dropna()

    duplicate_object_ids = None

    if "OBJECTID" in trails.columns:
        duplicate_object_ids = int(trails["OBJECTID"].duplicated().sum())

    return {
        "expected_record_count": expected_count,
        "downloaded_record_count": len(trails),
        "counts_match": len(trails) == expected_count,
        "crs": str(trails.crs),
        "geometry_types": geometry_types,
        "missing_geometry_count": trails.geometry.isna().sum(),
        "empty_geometry_count": non_missing_geometry.is_empty.sum(),
        "invalid_geometry_count": (~non_missing_geometry.is_valid).sum(),
        "duplicated_object_id_count": duplicate_object_ids,
        "missing_values": missing_values
    }