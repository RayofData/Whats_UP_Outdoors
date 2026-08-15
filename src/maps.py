"""Build interactive Folium maps for the Streamlit application."""

import folium

from src.locations import (
    zip_to_point,
)

UP_CENTER = [46.5, -87.5]


def build_trail_map(trails, zipcode = ""):
    """Build an interactive map of Upper Peninsula trails."""
    map_trails = trails.to_crs(epsg=4326).copy()

    if zipcode:
        zip_point = zip_to_point(zipcode)

        map_center = [
            zip_point.y,
            zip_point.x
        ]

        zoom_start = 9

    else: 
        map_center = UP_CENTER
        zoom_start = 7

    map_trails["Miles"] = map_trails["ReportedLengthMiles"].round(2)

    trail_map = map_trails.explore(
        location = map_center,
        zoom_start=zoom_start,
        tooltip=[
            "HikingName", 
            "County",
        ],
        tooltip_kwds={
            "aliases": [
                "Trail:",
                "County:"
            ]
        },
        popup=[
            "HikingName",
            "County",
            "Miles",
            "TrailWidth",
            "SurfaceTypes",
            "TrailStatuses"        
        ],
        popup_kwds={
            "aliases": [
                "Trail:",
                "County:",
                "Miles:",
                "Width:",
                "Surface:",
                "Status:"
            ]
        }
    )
    if zipcode:
        folium.Marker(
            location=map_center,
            tooltip=f"ZIP: {zipcode}"
        ).add_to(trail_map)

    return trail_map