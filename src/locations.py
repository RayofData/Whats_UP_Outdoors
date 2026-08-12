"""Handles logic for distance calculations"""

from pathlib import Path

import geopandas as gpd 
import pgeocode
from shapely.geometry import Point


PROCESSED_DIR = Path("data/processed")
PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"

MICHIGAN_GEOREF = "EPSG:3078"
METERS_PER_MILE = 1609.344

trails = gpd.read_parquet(PROCESSED_PATH)
trails_projected = trails.to_crs(MICHIGAN_GEOREF)



user_zipcode = "49781" #St. Ignace

zip_lookup = pgeocode.Nominatim("us")

location = zip_lookup.query_postal_code(user_zipcode)

user_point = Point(
    location.longitude,
    location.latitude
)

user_location = gpd.GeoDataFrame(
    {"zipcode": [user_zipcode]},
    geometry=[user_point],
    crs="EPSG:4326"
)
user_location_projected = user_location.to_crs(MICHIGAN_GEOREF)

user_point_projected = user_location_projected.geometry.iloc[0]

trails_projected["DistanceMiles"] = (
    trails_projected.geometry.distance(user_point_projected)
    / METERS_PER_MILE
)

print(
    trails_projected
    .sort_values("DistanceMiles")
    .head(5)
)

