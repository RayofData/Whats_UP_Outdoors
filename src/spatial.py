"""CRS transformations, distance calculations, radius filtering,
nearest-trail filtering, and related spatial operations."""

import geopandas as gpd


MICHIGAN_GEOREF = "EPSG:3078"
METERS_PER_MILE = 1609.344
MAX_TRAIL_RESULTS = 20
BUFFER_MILES = 2
SQ_METERS_PER_SQ_MILE = METERS_PER_MILE ** 2


def project_point(point):
    """Project a WGS 84 point to Michigan GeoRef."""
    point_series = gpd.GeoSeries([point], crs="EPSG:4326")

    return point_series.to_crs(MICHIGAN_GEOREF).iloc[0]


def distance_to_trails(trails, point):
    """Calculate point-to-trail distances in miles."""
    trails_projected = trails.to_crs(MICHIGAN_GEOREF)
    point_projected = project_point(point)

    return (
        trails_projected.geometry.distance(point_projected)
        / METERS_PER_MILE
    )


def find_nearby_trails(trails, user_point, radius_miles):
    """Filter trails to the selected radius around a ZIP-code point."""
    if trails.crs is None:
        raise ValueError("Trail GeoDataFrame must have a defined CRS.")

    results = trails.copy()
    results["DistanceMiles"] = distance_to_trails(results, user_point)

    results = results.loc[
        results["DistanceMiles"] <= radius_miles
    ]

    return (
        results
        .sort_values("DistanceMiles")
        .head(MAX_TRAIL_RESULTS)
        .copy()
    )


def distances_to_trail(trail, points):
    """Calculate observation-point distances to a selected trail in miles."""
    if trail.crs is None or points.crs is None:
        raise ValueError("Trail and observation GeoDataFrames must have a defined crs.")

    trail_projected = trail.to_crs(MICHIGAN_GEOREF)
    points_projected = points.to_crs(MICHIGAN_GEOREF)

    if len(trail) != 1:
        raise ValueError("Expected exactly one selected trail.")

    trail_geometry = trail_projected.geometry.iloc[0]

    return (
        points_projected.geometry.distance(trail_geometry)
        / METERS_PER_MILE
    )

def add_taxon_density_to_trails(trails, observations, buffer_miles = BUFFER_MILES):
    """Add nearby observation density by taxon group to each trail."""
    trails_projected = trails.to_crs(MICHIGAN_GEOREF).copy()
    observations_projected = observations.to_crs(MICHIGAN_GEOREF).copy()

    trail_buffers = trails_projected[["TrailGroupName", "geometry"]].copy()

    trail_buffers["geometry"] = trail_buffers.geometry.buffer(
        buffer_miles * METERS_PER_MILE
    )

    trail_buffers["BufferAreaSqMiles"] = (
        trail_buffers.geometry.area
        / SQ_METERS_PER_SQ_MILE
    )

    observations_with_trails = gpd.sjoin(
        observations_projected,
        trail_buffers[["TrailGroupName", "geometry"]],
        how="inner",
        predicate="within"
    )

    taxon_counts = (
        observations_with_trails
        .groupby(["TrailGroupName", "iconic_taxon"])
        .size()
        .unstack(fill_value=0)
    )

    taxon_counts = taxon_counts.reindex(
        columns=[
            "Aves",
            "Mammalia",
            "Plantae",
            "Fungi",
            "Reptilia",
            "Insecta",
        ],
        fill_value = 0
    )

    taxon_density = taxon_counts.div(
        trail_buffers
        .set_index("TrailGroupName")["BufferAreaSqMiles"],
        axis = "index"
    )

    taxon_density = taxon_density.rename(
        columns={
            "Aves": "BirdsPerSqMile",
            "Mammalia": "MammalsPerSqMile",
            "Plantae": "PlantsPerSqMile",
            "Fungi": "FungiPerSqMile",
            "Reptilia": "ReptilesPerSqMile",
            "Insecta": "InsectsPerSqMile",
        }
    )

    trails_with_density = trails.merge(
        taxon_density,
        on="TrailGroupName",
        how="left"
    )

    density_columns = [
        "BirdsPerSqMile",
        "MammalsPerSqMile",
        "PlantsPerSqMile",
        "FungiPerSqMile",
        "ReptilesPerSqMile",
        "InsectsPerSqMile",
    ]

    trails_with_density[density_columns] = (
        trails_with_density[density_columns]
        .fillna(0)
        .round(2)
    )

    return trails_with_density


def filter_observations_near_trail(trail, observations, buffer_miles = BUFFER_MILES):
    """Return observations within a specified milage of a trail"""
    distances = distances_to_trail(trail, observations)
    return observations.loc[distances <= buffer_miles].copy()


def create_trail_buffer(trail, buffer_miles = BUFFER_MILES):
    """Create buffer zone around trail for observation filter"""

    projected = trail.to_crs(MICHIGAN_GEOREF)
    buffer_meters = buffer_miles * METERS_PER_MILE

    trail_buffer = gpd.GeoDataFrame(
        projected[["TrailGroupName"]].copy(),
        geometry=projected.geometry.buffer(buffer_meters),
        crs=MICHIGAN_GEOREF
    )

    return trail_buffer