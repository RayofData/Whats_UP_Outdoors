"""Build interactive Folium maps for the Streamlit application."""

import folium
from folium.plugins import FeatureGroupSubGroup

from src.locations import (
    zip_to_point,
)

from src.inaturalist import (
    TAXON_GROUPS
)

UP_CENTER = [46.5, -87.5]
RECENT_COLOR = "orange"
HISTORICAL_COLOR = "cadetblue"

TAXON_ICONS = {
    "Aves": "crow",
    "Mammalia": "paw",
    "Plantae": "leaf",
    "Fungi": "seedling",
    "Reptilia": "dragon",
    "Insecta": "bug",
}

TAXON_LABEL = {
    taxon_name: display_name
    for display_name, taxon_name in TAXON_GROUPS.items()
}


def build_trail_map(trails, zip_point=None):
    """Build an interactive map of Upper Peninsula trails."""
    map_trails = trails.to_crs(epsg=4326).copy()

    if zip_point is not None:
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
    if zip_point is not None:
        folium.Marker(
            location=[zip_point.y, zip_point.x]
        ).add_to(trail_map)

    return trail_map


def build_observation_map(selected_trail, recent_observations, historical_observations):
    """Build an interactive map centered on the complete selected trail."""
    map_trail = selected_trail.to_crs(epsg=4326).copy()
    map_recent = recent_observations.to_crs(epsg=4326).copy()
    map_history = historical_observations.to_crs(epsg=4326).copy()

    taxon_totals = (
        map_recent["iconic_taxon"]
        .value_counts()
        .add(
            map_history["iconic_taxon"].value_counts(),
            fill_value=0
        )
        .astype(int)
        .to_dict()
    )

    observation_groups = [
        (map_recent, RECENT_COLOR),
        (map_history, HISTORICAL_COLOR)
    ]

    west, south, east, north = map_trail.total_bounds

    observation_map = folium.Map(
        tiles="OpenStreetMap",
        control_scale=True
    )

    folium.GeoJson(
        map_trail
    ).add_to(observation_map)


    for observations, marker_color in observation_groups:
        for _, observation in observations.iterrows():
            taxon_name = observation["iconic_taxon"]

            taxon_label = TAXON_LABEL.get(
                taxon_name,
                "Unknown"
            )

            taxon_total = taxon_totals.get(
                taxon_name,
                0
            )

            folium.Marker(
                location=[
                    observation.geometry.y,
                    observation.geometry.x
                ],
                icon=folium.Icon(
                    color=marker_color,
                    icon=TAXON_ICONS.get(
                        taxon_name,
                        "circle"
                    ),
                    prefix="fa"
                ),
                tooltip=(
                    f"{observation["common_name"]}"
                ),
            popup=(
                f'{observation["common_name"]} | '
                f'{observation["observed_on"].date()} | '
                f'Total {taxon_label}: {taxon_total}'
            )
        ).add_to(observation_map)

    observation_map.fit_bounds(
        [
            [south, west],
            [north, east]
        ],
        padding=(30,30),
        max_zoom=15
    )

    return observation_map