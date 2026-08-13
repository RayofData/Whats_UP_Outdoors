"""Convert the historical iNaturalist CSV export to compressed Parquet"""

from pathlib import Path

import pandas as pd 

from src.inaturalist import TAXON_GROUPS

PROJECT_ROOT = Path(__file__).resolve().parent


RAW_PATH = (
    PROJECT_ROOT 
    / "data" 
    / "raw" 
    / "inaturalist_up_fall_observations_2015_2025.csv"
)

PROCESSED_PATH = (
    PROJECT_ROOT 
    / "data" 
    / "processed" 
    / "inaturalist_up_fall_observations.parquet"
)

COLUMNS = [
        "id",
        "observed_on",
        "quality_grade",
        "image_url",
        "latitude",
        "longitude",
        "common_name",
        "iconic_taxon_name",
        "taxon_species_name",
    ]

up_historical = pd.read_csv(RAW_PATH, usecols=COLUMNS)

up_historical["observed_on"] = pd.to_datetime(
    up_historical["observed_on"],
    errors="coerce"
)

up_historical = up_historical.rename(
        columns={
            "id": "observation_id",
            "image_url": "thumbnail_url",
            "iconic_taxon_name": "iconic_taxon",
            "taxon_species_name": "scientific_name",
        }
    )
up_historical = up_historical.loc[
    up_historical["iconic_taxon"].isin(TAXON_GROUPS.values())
    & up_historical["scientific_name"].notna()
    & up_historical["latitude"].notna()
    & up_historical["longitude"].notna()
].copy()

up_historical = up_historical.drop_duplicates(subset="observation_id")

up_historical.to_parquet(
    PROCESSED_PATH,
    index = False,
    compression="zstd"
)

print(f"Observations saved: {len(up_historical):,}")
print(f"Saved to: {PROCESSED_PATH}")
