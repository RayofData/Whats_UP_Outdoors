import requests
import pandas as pd 

LAYER_URL = (
    "https://gisagodnr.state.mi.us/arcgis/rest/services/"
    "DNR/DNRTrailsOPENDATA/MapServer/2"
)

QUERY_URL = f"{LAYER_URL}/query"

WHERE_CLAUSE = "Peninsula = 'Upper Peninsula'"
BATCH_SIZE = 500

DOWNLOAD_FIELDS = [
    "OBJECTID",
    "DNRTrail",
    "TrailNamePrimary",
    "HikingName",
    "FacilityName",
    "County",
    "Peninsula",
    "Hiking",
    "TrailUseCategory",
    "OpenClosedStatusNonmotor",
    "SurfaceType",
    "TrailWidthFeet",
    "ADAAccessible",
    "SegmentLengthMiles"
]

DROP_COLUMNS = [
    "Peninsula",
    "DNRTrail",
    "Hiking"
]

PLACEHOLDER_VALUES = {
    "",
    "-1",
    "-2",
    "99",
    "-99",
    "Unspecified",
    "Unknown",
    "None",
    "N/A",
    "<NA>",
    "NA"
}

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
        raise RuntimeError("GeoJSON response did not contain a features field")

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

    missing_values = {}

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
        "missing_geometry_count": int(trails.geometry.isna().sum()),
        "empty_geometry_count": int(non_missing_geometry.is_empty.sum()),
        "invalid_geometry_count": int((~non_missing_geometry.is_valid).sum()),
        "duplicated_object_id_count": duplicate_object_ids,
        "missing_values": missing_values
    }

def validate_download(trails, expected_object_ids):
    """Check that the basic trail download looks complete."""

    if trails.empty:
        raise RuntimeError("Downloaded trail data is empty.")

    if "OBJECTID" not in trails.columns:
        raise RuntimeError("Downloaded data does not contain OBJECTID.")

    downloaded_ids = set(trails["OBJECTID"].dropna().astype(int))
    expected_ids = set(expected_object_ids)

    missing_ids = expected_ids - downloaded_ids
    unexpected_ids = downloaded_ids - expected_ids

    if missing_ids:
        preview = sorted(missing_ids)[:10]
        raise RuntimeError(
            f"{len(missing_ids)} object IDs were not downloaded. "
            f"First missing IDs: {preview}"
        )
    
    if unexpected_ids:
        preview = sorted(unexpected_ids)[:10]
        raise RuntimeError(
            f"{len(unexpected_ids)} unexpected object IDs appeared. "
            f"First unexpected IDs: {preview}"
        )

def replace_missing_placeholders(trails):
    """Replace text placeholder values  with pd.NA and return a clean copy."""

    cleaned = trails.copy()

    text_columns = cleaned.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        cleaned_trails = cleaned[column].astype("string").str.strip()

        cleaned[column] = cleaned_trails.mask(
            cleaned_trails.isin(PLACEHOLDER_VALUES),
            pd.NA
        )
    return cleaned

def prep_columns(trails):
    """Drop unused columns and create the trail grouping key."""

    cleaned_trails = trails.drop(
        columns=DROP_COLUMNS
    ).copy()

    cleaned_trails["TrailGroupName"] = (
        cleaned_trails["County"]
        + " | "
        + cleaned_trails["HikingName"]
    )

    return cleaned_trails


def aggregate_column(column):
    """Summarize string columns values for a grouped trail."""

    valid_values = column.dropna().unique()

    if len(valid_values) == 0:
        return "Unknown"
    
    if len(valid_values) == 1:
        return valid_values[0]
    
    return "Varies"