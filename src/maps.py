"""Build interactive Folium maps for the Streamlit application."""

import geopandas as gpd

UP_CENTER = [46.5, -87.5]


def build_trail_map(trails):
    """Build an interactive map of Upper Peninsula trails."""
    map_trails = trails.to_crs(epsg=4326).copy()

    map_trails["Miles"] = map_trails["ReportedLengthMiles"].round(2)

    return map_trails.explore(
        location = UP_CENTER,
        zoom_start=6,
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