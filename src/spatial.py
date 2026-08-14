"""CRS transformations, distance calculations, radius filtering,
nearest-trail filtering, and related spatial operations."""

import geopandas as gpd


MICHIGAN_GEOREF = "EPSG:3078"
METERS_PER_MILE = 1609.344
MAX_TRAIL_RESULTS = 20


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


def filter_observations_near_trail(trail, observations, miles = 2):
    """Return observations within a specified milage of a trail"""
    distances = distances_to_trail(trail, observations)
    return observations.loc[distances <= miles].copy()