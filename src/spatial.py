"""CRS transformations, distance calculations, radius filtering,
nearest-trail filtering, and related spatial operations."""

import geopandas as gpd


MICHIGAN_GEOREF = "EPSG:3078"
METERS_PER_MILE = 1609.344
MAX_TRAIL_RESULTS = 20


def project_point(point):
    """Reproject a Shapely point between coordinate reference systems."""
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