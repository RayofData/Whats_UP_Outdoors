"""ZIP normalization, validation, `pgeocode` lookup, and user point creation."""

import re

import pandas as pd
import pgeocode
from shapely.geometry import Point



ZIP_LOOKUP = pgeocode.Nominatim("us")
ZIP_PATTERN = re.compile(r"^\d{5}$")

def normalize_zipcode(zipcode):
    """Normalize and validate a five-digit U.S. ZIP code."""
    normalized_zipcode = str(zipcode).strip()

    if not ZIP_PATTERN.fullmatch(normalized_zipcode):
        raise ValueError("ZIP code must contain exactly 5 digits.")

    return normalized_zipcode



def zip_to_point(zipcode):
    """Converts ZIP code to longitude and latitude point."""

    normalized_zipcode = normalize_zipcode(zipcode)

    location = ZIP_LOOKUP.query_postal_code(normalized_zipcode)

    if pd.isna(location.latitude) or pd.isna(location.longitude):
        raise ValueError("ZIP code could not be resolved.")

    return Point(location.longitude, location.latitude)