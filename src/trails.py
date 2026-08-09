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