"""Defines the Streamlit user interface for What's UP Outdoors."""

from pathlib import Path

import streamlit as st
import geopandas as gpd 
from streamlit_folium import st_folium

from src.maps import build_trail_map
from src.locations import normalize_zipcode, zip_to_point
from src.spatial import find_nearby_trails, distance_to_trails, VALID_SEARCH_RADII

st.set_page_config(page_title="What's UP Outdoors")


PROJECT_ROOT = Path(__file__).resolve().parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"

STATIC_DIR = PROJECT_ROOT / "static"
MAP_IMAGE_PATH = STATIC_DIR / "map_up.jpg"
BANNER_PATH = STATIC_DIR / "banner.png"

trails = gpd.read_parquet(PROCESSED_PATH)

st.sidebar.title("What's UP Outdoors")
st.sidebar.write("A Python and Streamlit portfolio project for discovering hiking "
                    "trails and nearby iNaturalist observations in Michigan’s Upper Peninsula. "
                    "Enter any UP zipcode, use map if needed.")

st.sidebar.image(MAP_IMAGE_PATH)
zipcode = st.sidebar.text_input("Enter UP Zipcode: ")
radius = st.sidebar.radio("Search Radius: ", VALID_SEARCH_RADII, horizontal = True)
nearby_trails = trails.copy()

if zipcode:
    normal_zip = normalize_zipcode(zipcode)
    zip_point = zip_to_point(normal_zip)
    
    nearby_trails = find_nearby_trails(
        nearby_trails, 
        zip_point, 
        radius
    )

    nearby_trails["DistanceToTrailMiles"] = distance_to_trails(nearby_trails, zip_point)


st.image(BANNER_PATH)
st.subheader("What's UP Outdoors: Upper Peninsula Trail Explorer")

tab1, tab2, tab3 = st.tabs([
    "Discover Trails",
    "Trail Map",
    "Trail Details",
])

st.divider()

with tab1:

    st.dataframe(
        nearby_trails,
        column_order=[
            "HikingName",
            "County",
            "DistanceToTrailMiles",
            "LengthCategory",
            "ReportedLengthMiles",
            "TrailWidth",
            "SurfaceTypes",
            "TrailStatuses",

        ],
        column_config={
            "HikingName": "Trail",
            "LengthCategory": "Length Category",
            "DistanceToTrailMiles": "Distance to Trail (Miles)",
            "ReportedLengthMiles": "Length (Miles)",
            "TrailWidth": "Width",
            "SurfaceTypes": "Surface",
            "TrailStatuses": "Status",

        },
        hide_index=True,
    )

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
    st.write("Select trail tab")



if zipcode:
    st.write(f"You have entered zipcode: {zipcode}")

st.divider()