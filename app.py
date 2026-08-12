"""Defines the Streamlit user interface for What's UP Outdoors."""

from pathlib import Path

import streamlit as st
import geopandas as gpd 
from streamlit_folium import st_folium

from src.maps import build_trail_map

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

st.image(BANNER_PATH)
st.subheader("What's UP Outdoors: Upper Peninsula Trail Explorer")

st.divider()
st.dataframe(trails)

st.divider()
trail_map = build_trail_map(trails)
st_folium(trail_map, height=300)

st.divider()
st.subheader("Metrics")
st.metric(label="Total Trails", value=len(trails))

if zipcode:
    st.write(f"You have entered zipcode: {zipcode}")

st.divider()