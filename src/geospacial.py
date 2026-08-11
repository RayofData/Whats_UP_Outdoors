from pathlib import Path

import geopandas as gpd 

PROCESSED_DIR = Path("data/processed")
PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"

trails = gpd.read_parquet(PROCESSED_PATH)