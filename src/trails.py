"""Clean, normalize, group, and summarize trail data."""

import pandas as pd 

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
    "None",
    "N/A",
    "<NA>",
    "NA"
}

TRAIL_NAME_ALIASES = {
    # Alger
    (
        "Alger",
        "Laughing Whitefish Falls - Trails",
    ): "Laughing Whitefish Falls Trails",

    # Gogebic
    (
        "Gogebic",
        "Ironwood To Bessemer",
    ): "Ironwood to Bessemer State Trail",
    (
        "Gogebic",
        "Porcupine Mountain Wilderness - Lake Superior Trail",
    ): "Porcupine Mountain Wilderness Lake Superior Trail",
    (
        "Gogebic",
        "Porcupine Mts Lake Superior Trail",
    ): "Porcupine Mountain Wilderness Lake Superior Trail",
    (
        "Gogebic",
        "Porcupine Mountain Wilderness - Pinkerton Trail",
    ): "Porcupine Mountain Wilderness Pinkerton Trail",
    (
        "Gogebic",
        "Porcupine Mts Cross Trail Correction Line Trail",
    ): "Porcupine Mountain Wilderness Cross Trail Correction Line Trail",

    # Marquette
    (
        "Marquette",
        "Van Riper - Main Trail",
    ): "Van Riper Main Trail",
    (
        "Marquette",
        "Van Riper - Old Wagon Road Trail",
    ): "Van Riper Old Wagon Road Trail",
    (
        "Marquette",
        "Van Riper - River Trail",
    ): "Van Riper River Trail",

    # Ontonagon
    (
        "Ontonagon",
        "Porcupine Mountain Wilderness - Beaver Creek Trail",
    ): "Porcupine Mountain Wilderness Beaver Creek Trail",
    (
        "Ontonagon",
        "Porcupine Mountain Wilderness - Escarpment Trail",
    ): "Porcupine Mountain Wilderness Escarpment Trail",
    (
        "Ontonagon",
        "Porcupine Mts Escarpment Trail",
    ): "Porcupine Mountain Wilderness Escarpment Trail",
    (
        "Ontonagon",
        "Porcupine Mountain Wilderness - Lake Superior Trail",
    ): "Porcupine Mountain Wilderness Lake Superior Trail",
    (
        "Ontonagon",
        "Porcupine Mts Lake Superior Trail",
    ): "Porcupine Mountain Wilderness Lake Superior Trail",
    (
        "Ontonagon",
        "Porcupine Mountain Wilderness - Lost Lake Trail",
    ): "Porcupine Mountain Wilderness Lost Lake Trail",
    (
        "Ontonagon",
        "Porcupine Mts Lost Lake Trail",
    ): "Porcupine Mountain Wilderness Lost Lake Trail",
    (
        "Ontonagon",
        "Porcupine Mountain Wilderness - South Mirror Lake Trail",
    ): "Porcupine Mountain Wilderness South Mirror Lake Trail",
    (
        "Ontonagon",
        "Porcupine Mountain Wilderness - Union Spring Trail",
    ): "Porcupine Mountain Wilderness Union Spring Trail",
    (
        "Ontonagon",
        "Porcupine Mts Big Carp River Trail",
    ): "Porcupine Mountain Wilderness Big Carp River Trail",
    (
        "Ontonagon",
        "Porcupine Mountains Correction Line Trail",
    ): "Porcupine Mountain Wilderness Cross Trail Correction Line Trail",
    (
        "Ontonagon",
        "Porcupine Mts Cross Trail Correction Line Trail",
    ): "Porcupine Mountain Wilderness Cross Trail Correction Line Trail",
}


def replace_missing_placeholders(trails):
    """Replace text placeholder values  with pd.NA and return a clean copy."""

    cleaned = trails.copy()

    text_columns = cleaned.select_dtypes(
        include = ["object", "string"]
    ).columns

    for column in text_columns:
        cleaned_column = cleaned[column].astype("string").str.strip()

        cleaned[column] = cleaned_column.mask(
            cleaned_column.isin(PLACEHOLDER_VALUES),
            pd.NA
        )
    return cleaned

def aggregate_column(column):
    """Summarize string columns values for a grouped trail."""

    valid_values = column.dropna().unique()

    if len(valid_values) == 0:
        return "Unknown"
    
    if len(valid_values) == 1:
        return valid_values[0]
    
    return "Varies"

def combine_unique(values):
    """Combine unique non-missing values into one readable string."""
    unique_values = sorted(
        {
            str(value).strip()
            for value in values.dropna()
            if str(value).strip()
        }
    )

    return ", ".join(unique_values) if unique_values else "Unknown"

def normalize_trail_name(county, hiking_name):
    """Return the canonical hiking-trail name for known aliases."""

    return TRAIL_NAME_ALIASES.get(
        (county, hiking_name),
        hiking_name
    )

def prep_columns(trails):
    """Prepare columns and create the trail grouping key."""

    cleaned_trails = trails.drop(
        columns = DROP_COLUMNS
    ).copy()

    cleaned_trails["HikingName"] = [
        normalize_trail_name(county, hiking_name)
        for county, hiking_name in zip(
            cleaned_trails["County"],
            cleaned_trails["HikingName"]
        )
    ]

    cleaned_trails["TrailGroupName"] = (
        cleaned_trails["County"]
        + " | "
        + cleaned_trails["HikingName"]
    )

    return cleaned_trails


def group_trails(trails):
    """Group trail segments by county and trail name"""
    
    grouped_trails = (
        trails.dissolve(
            by="TrailGroupName",
            aggfunc={
                "HikingName": "first",
                "County": "first",
                "FacilityName": combine_unique,
                "SegmentLengthMiles": "sum",
                "SurfaceType": combine_unique,
                "OpenClosedStatusNonmotor": combine_unique,
                "TrailWidthFeet": aggregate_column,
                "ADAAccessible": combine_unique,
                "OBJECTID": "count"
            },
        )
        .reset_index()
        .rename(
            columns={
                "SegmentLengthMiles": "ReportedLengthMiles",
                "SurfaceType": "SurfaceTypes",
                "OpenClosedStatusNonmotor": "TrailStatuses",
                "TrailWidthFeet": "TrailWidth",
                "ADAAccessible": "AccessibilityValues",
                "OBJECTID": "SegmentCount",            
            }
        )
    )

    return grouped_trails

def add_length_category(trails):
    """Add short, medium, and long trail-length categories using DNR-reported trail lengths."""

    categorized = trails.copy()

    categorized["LengthCategory"] = pd.cut(
        categorized["ReportedLengthMiles"],
        bins=[0,2,7, float("inf")],
        labels = ["Short", "Medium", "Long"],
        include_lowest=True,
        right=True
    )

    return categorized