"""Convert the historical iNaturalist CSV export to compressed Parquet"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.inaturalist import (
    INATURALIST_EXPORT_COLUMNS,
    TAXON_GROUPS,
    normalize_observation_columns
)


RAW_PATH_UP = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "inaturalist_up_fall_observations_2015_2025.csv"
)

RAW_PATH_LP = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "inaturalist_lp_fall_observations_2015_2025.csv"
)

PROCESSED_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inaturalist_historical_fall_observations.parquet"
)


def prepare_historical_observations(observations):
    """Clean and normalize historical iNaturalist observations."""
    observations = normalize_observation_columns(observations)

    observations["observed_on"] = pd.to_datetime(
        observations["observed_on"],
        errors="coerce"
    )

    for column in ["latitude", "longitude"]:
        observations[column] = pd.to_numeric(
            observations[column],
            errors="coerce"
        )

    observations = observations.loc[
        observations["latitude"].between(-90, 90)
        & observations["longitude"].between(-180, 180)
    ].copy()

    observations["scientific_name"] = (
        observations["scientific_name"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    observations = observations.loc[
        observations["iconic_taxon"].isin(TAXON_GROUPS.values())
        & observations["scientific_name"].notna()
        & observations["latitude"].notna()
        & observations["longitude"].notna()
        & observations["observed_on"].notna()
        & observations["observation_id"].notna()
    ].copy()

    observations = observations.drop_duplicates(subset="observation_id")


    return observations

def load_historical_export(path):
    """Read either export format and report schema errors with the source path."""
    observations = pd.read_csv(
        path,
        usecols=lambda column: column in INATURALIST_EXPORT_COLUMNS,
    )
    try:
        return prepare_historical_observations(observations)
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc


def main():
    mi_historical = pd.concat(
        [load_historical_export(path) for path in (RAW_PATH_UP, RAW_PATH_LP)],
        ignore_index=True,
    ).drop_duplicates(subset="observation_id", ignore_index=True)

    try:
        PROCESSED_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )
    except OSError as exc:
        raise RuntimeError(
            f"Could not create output directories: {exc}"
        ) from exc


    if not mi_historical.empty:
        mi_historical.to_parquet(
            PROCESSED_PATH,
            index = False,
            compression="zstd"
        )
    else:
        raise ValueError(
            "Historical observation processing produced no records."
        )

    print(f"Observations saved: {len(mi_historical):,}")
    print(f"Saved to: {PROCESSED_PATH}")

if __name__ == "__main__":
    main()
