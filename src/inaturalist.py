"""iNaturalist helpers for API and historical data loading."""

import geopandas as gpd 


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
