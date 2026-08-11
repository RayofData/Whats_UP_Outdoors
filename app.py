from pathlib import Path
import os

import streamlit as st
import geopandas as gpd 

st.set_page_config(page_title="What's UP Outdoors")

PROCESSED_DIR = Path("data/processed")
PROCESSED_PATH = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"

trails = gpd.read_parquet(PROCESSED_PATH)

st.sidebar.title("What's UP Outdoors")
st.sidebar.write("A Python and Streamlit portfolio project for discovering hiking "
                    "trails and nearby iNaturalist observations in Michigan’s Upper Peninsula. "
                    "Enter any UP zipcode, use map if needed.")

st.sidebar.image(os.path.join(os.getcwd(), "static", "map_up.jpg"))
zipcode = st.sidebar.text_input("Enter UP Zipcode: ")

st.image(os.path.join(os.getcwd(), "static", "banner.png"))
st.subheader("What's UP Outdoors: Upper Peninsula Trail Explorer")

st.divider()

st.dataframe(trails.head(10))

st.divider()

st.subheader("Metrics")
st.metric(label="Total Trails", value=len(trails))

if zipcode:
    st.write(f"You have entered zipcode: {zipcode}")

st.divider()