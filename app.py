"""Defines the Streamlit user interface for What's UP Outdoors."""

from pathlib import Path

import streamlit as st
import geopandas as gpd 
from streamlit_folium import st_folium

from src.locations import (
    normalize_zipcode, 
    zip_to_point,
    get_zip_info
)
from src.spatial import (
    find_nearby_trails, 
    distance_to_trails, 
    VALID_SEARCH_RADII
)
from src.maps import build_trail_map

PROJECT_ROOT = Path(__file__).resolve().parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"

STATIC_DIR = PROJECT_ROOT / "static"
MAP_IMAGE_PATH = STATIC_DIR / "map_up.jpg"
BANNER_PATH = STATIC_DIR / "banner.png"

trails = gpd.read_parquet(PROCESSED_PATH)

st.set_page_config(page_title = "What's UP Outdoors.", initial_sidebar_state = "expanded", layout="wide")
st.sidebar.title("What's UP Outdoors")
st.sidebar.write(
    "Discover hiking trails across Michigan’s Upper Peninsula and explore nearby "
    "iNaturalist observations."
)

st.sidebar.caption(
    "Enter a ZIP code and choose a search radius to find nearby trails."
)
st.sidebar.image(MAP_IMAGE_PATH)

def reset_search():
    """Resets zip to reset table"""
    st.session_state.zipcode = ""

zipcode = st.sidebar.text_input("Enter UP Zipcode: ", key="zipcode")
radius = st.sidebar.radio("Search Radius: ", VALID_SEARCH_RADII, horizontal = True)
st.sidebar.button("Reset to all trails.", on_click=reset_search)

if zipcode: 
    zip_info = get_zip_info(zipcode)
    st.sidebar.markdown(
        f"""
    **ZIP:** {zip_info["zipcode"]}  
    **City:** {zip_info["place"]}  
    **County:** {zip_info["county"]}  
    **State:** {zip_info["state"]}
    """
    )     


nearby_trails = trails.copy()
search_completed = False


if zipcode:
    try: 
        normal_zip = normalize_zipcode(zipcode)
        zip_point = zip_to_point(normal_zip)
    
        nearby_trails = find_nearby_trails(
            nearby_trails, 
            zip_point, 
            radius
        )

        nearby_trails["DistanceToTrailMiles"] = distance_to_trails(nearby_trails, zip_point)
        search_completed = True

    except ValueError as exc:
        st.sidebar.error(str(exc))

def display_trails_dataframe(trails, selectable=False):
    """Display trail data with readable Streamlit column formatting."""
    dataframe_options = {
        "column_order": [
            "HikingName",
            "County",
            "DistanceToTrailMiles",
            "LengthCategory",
            "ReportedLengthMiles",
            "TrailWidth",
            "SurfaceTypes",
            "TrailStatuses",
        ],
        "column_config": {
            "HikingName": "Trail",
            "County": "County",
            "DistanceToTrailMiles": "Distance to Trail (Miles)",
            "LengthCategory": "Length Category",
            "ReportedLengthMiles": "Length (Miles)",
            "TrailWidth": "Width",
            "SurfaceTypes": "Surface",
            "TrailStatuses": "Status",
        },
        "hide_index": True,
    }

    if selectable:
        dataframe_options.update({
            "on_select": "rerun",
            "selection_mode": "single-row",
            "key": "selection",
        })

    return st.dataframe(
        trails,
        **dataframe_options,
    )


st.image(BANNER_PATH)
st.subheader("What's UP Outdoors: Upper Peninsula Trail Explorer")

tab1, tab2, tab3 = st.tabs([
    "Discover Trails",
    "Trail Map",
    "Trail Details",
])

st.divider()

with tab1:
    selected_rows = None
    if search_completed and nearby_trails.empty:
        st.info(f"No trails found within {radius} miles.")

    else: 
        event = display_trails_dataframe(nearby_trails, selectable=True)

        selected_rows = event.selection.rows

        st.divider()
        st.subheader("Metrics")
        st.metric(label="Total Trails", value=len(nearby_trails))

with tab2: 
    trail_map = build_trail_map(nearby_trails)
    st_folium(trail_map, height=300)

    st.divider()
    st.subheader("Metrics")
    st.metric(label="Total Trails", value=len(nearby_trails))

with tab3:
    if selected_rows:
        row_idx = selected_rows[0]
        selected_data = nearby_trails.iloc[[row_idx]]

        display_trails_dataframe(selected_data, selectable=False)

    else:
        st.info("Click on a trail in tab 1 to see details.")


st.divider()