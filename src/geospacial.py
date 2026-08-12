

from pathlib import Path

import geopandas as gpd 
import pgeocode
from shapely.geometry import Point


PROCESSED_DIR = Path("data/processed")
PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"

MICHIGAN_GEOREF = "EPSG:3078"

trails = gpd.read_parquet(PROCESSED_PATH)

zip_lookup = pgeocode.Nominatim("us")

user_zipcode = "49781"

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

trails_projected = trails.to_crs(MICHIGAN_GEOREF)

