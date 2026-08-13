import geopandas as gpd
import pytest
from shapely.geometry import LineString, Point 

from src.spatial import distance_to_trails, find_nearby_trails

one_mile_meters = 1609.344


def make_trail(projected_point, distance_miles):
    distance_meters = distance_miles * one_mile_meters
    
    return LineString(
        [
            (
                projected_point.x + distance_meters,
                projected_point.y - 1000,
            ),
            (
                projected_point.x + distance_meters,
                projected_point.y + 1000
            )
        ]
    )

def test_distance_to_trails_returns_one_mile():
    """Point-to-trail distance should be approximately one mile."""
    user_point = Point(-84.7, 46.0)
    projected_point = (
        gpd.GeoSeries(
            [user_point],
            crs="EPSG:4326"
        )
        .to_crs("EPSG:3078")
        .iloc[0]
    )

    trail = make_trail(projected_point, 1)

    trails = gpd.GeoDataFrame(
        {
            "HikingName": ["Test Trail"],
        },
            geometry=[trail],
            crs="EPSG:3078"
    )

    distances = distance_to_trails(
        trails,
        user_point
    )

    result = distances.iloc[0]

    assert result == pytest.approx(1.0)

def test_find_nearby_trails_filters_and_sorts():
    """Trails should be filtered by radius and ordered nearest first."""
    user_point = Point(-84.7, 46.0)
    projected_point = (
        gpd.GeoSeries(
            [user_point],
            crs="EPSG:4326",
        )
        .to_crs("EPSG:3078")
        .iloc[0]
    )



    trails = gpd.GeoDataFrame(
        {
            "HikingName": [
                "Two Mile Trail",
                "Eight Mile Trail",
                "Twelve Mile Trail"
            ]
        },
        geometry=[
            make_trail(projected_point, 2),
            make_trail(projected_point, 8),
            make_trail(projected_point, 12)            
        ],
        crs="EPSG:3078"
    )

    results = find_nearby_trails(
        trails,
        user_point,
        radius_miles=10
    )

    assert len(results) == 2
    assert results["HikingName"].tolist() == [
        "Two Mile Trail",
        "Eight Mile Trail"
    ]
    assert results["DistanceMiles"].tolist() == pytest.approx(
        [2.0, 8.0]
    )


def test_find_nearby_trails_limits_results():
    """Trails should be limited to only 20 results."""
    user_point = Point(-84.7, 46.0)
    projected_point = (
        gpd.GeoSeries(
            [user_point],
            crs="EPSG:4326",
        )
        .to_crs("EPSG:3078")
        .iloc[0]
    )

    trails = gpd.GeoDataFrame(
        {
            "HikingName": [
                f"{distance} Mile Trail"
                for distance in range(5,35)
            ]
        },
        geometry=[
            make_trail(projected_point, distance)
            for distance in range(5,35)
        ],
        crs="EPSG:3078"
    )

    results = find_nearby_trails(
        trails,
        user_point,
        radius_miles=50
    )

    assert len(results) == 20
    