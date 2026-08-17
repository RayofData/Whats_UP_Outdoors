"""iNaturalist observation processing, normalization, grouping, and summary utilities."""

import geopandas as gpd 
import pandas as pd


TAXON_GROUPS = {
    "Birds": "Aves",
    "Mammals": "Mammalia",
    "Plants": "Plantae",
    "Fungi": "Fungi",
    "Reptiles": "Reptilia",
    "Insects": "Insecta",
}

INATURALIST_EXPORT_COLUMNS = [
    "id",
    "observed_on",
    "image_url",
    "latitude",
    "longitude",
    "common_name",
    "iconic_taxon_name",
    "taxon_species_name",
]

OBSERVATION_COLUMN_RENAMES = {
    "id": "observation_id",
    "iconic_taxon_name": "iconic_taxon",
    "taxon_species_name": "scientific_name",
}

OBSERVATION_COLUMNS = [
    "observation_id",
    "observed_on",
    "common_name",
    "scientific_name",
    "iconic_taxon",
    "image_url",
    "longitude",
    "latitude",
]

OBSERVATION_DISPLAY_COLUMNS = [
    "image_url",
    "observed_count",
    "common_name",
    "most_recent",
]

def normalize_observation_columns(observations):
    """Normalize observation columns to the common application schema."""
    normalized = observations.rename(
        columns=OBSERVATION_COLUMN_RENAMES
    )
    return normalized[OBSERVATION_COLUMNS].copy()


def normalize_recent_observations(observations):
    """Flatten iNaturalist API results into the common observation schema."""
    if not isinstance(observations, list):
        raise ValueError("Recent iNaturalist observations must be a list.")

    rows = []

    for observation in observations:
        if not isinstance(observation, dict):
            continue

        taxon = observation.get("taxon") or {}
        geojson = observation.get("geojson") or {}
        coordinates = geojson.get("coordinates") or []

        if len(coordinates) < 2:
            longitude = None
            latitude = None
        else:
            longitude, latitude = coordinates[:2]

        photos = observation.get("photos") or []
        photo = photos[0] if photos and isinstance(photos[0], dict) else {}

        rows.append({
            "observation_id": observation.get("id"),
            "observed_on": observation.get("observed_on"),
            "common_name": (
                taxon.get("preferred_common_name")
                or observation.get("species_guess")
                or taxon.get("name")
            ),
            "scientific_name": taxon.get("name"),
            "iconic_taxon": taxon.get("iconic_taxon_name"),
            "image_url": (
                photo.get("url", "").replace("/square.","/medium.")
            if photo.get("url")
            else None
        ),
            "longitude": longitude,
            "latitude": latitude,
        })

    normalized = pd.DataFrame(rows, columns=OBSERVATION_COLUMNS)
    normalized["observed_on"] = pd.to_datetime(
        normalized["observed_on"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    for column in ["longitude", "latitude"]:
        normalized[column] = pd.to_numeric(
            normalized[column],
            errors="coerce"
        )

    normalized = normalized.loc[
        normalized["iconic_taxon"].isin(TAXON_GROUPS.values())
        & normalized["scientific_name"].notna()
        & normalized["observation_id"].notna()
        & normalized["observed_on"].notna()
        & normalized["longitude"].between(-180, 180)
        & normalized["latitude"].between(-90, 90)
    ].drop_duplicates(subset="observation_id")

    return convert_to_geodataframe(normalized)


def convert_to_geodataframe(observations):
    """Convert observations to a WGS 84 GeoDataFrame with Point geometry."""
    observations = gpd.GeoDataFrame(
        observations.copy(),
        geometry=gpd.points_from_xy(
            observations["longitude"],
            observations["latitude"]
        ),
        crs="EPSG:4326"
    )

    return observations


def split_observations_by_taxon(observations):
    """Split observations into DataFrames by supported taxon group."""
    return {
        display_name: observations.loc[
            observations["iconic_taxon"] == taxon_name
        ].copy()
        for display_name, taxon_name in TAXON_GROUPS.items()
    }


def summarize_species(observations):
    """Return the top 10 species by count, breaking ties by recent date."""

    summary = (
        observations.groupby("scientific_name", as_index=False)
        .agg(
            observed_count=("scientific_name","size"),
            most_recent=("observed_on", "max"),
            common_name=("common_name", "first"),
            image_url=("image_url", "first")
        )
        .sort_values(
            ["observed_count", "most_recent"],
            ascending=[False,False]
        )
        .head(10)
        .copy()
    )

    return summary

def limit_observations(observations, limit=25):
    """Return up to a set number of observations from each TAXON group to help load map"""
    return(
        observations
        .sort_values("observed_on", ascending=False)
        .groupby("iconic_taxon", group_keys=False)
        .head(limit)
    )
