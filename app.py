"""Defines the Streamlit user interface for What's UP Outdoors."""

from pathlib import Path

import streamlit as st
import geopandas as gpd 
import pandas as pd
from streamlit_folium import st_folium

from src.trails import (
    filter_trails
)

from src.locations import (
    normalize_zipcode, 
    zip_to_point,
    get_zip_info
)
from src.spatial import (
    find_nearby_trails, 
    distance_to_trails,
    distances_to_trail
)
from src.spatial import (
    filter_observations_near_trail
)
from src.maps import (
    build_trail_map
)
from src.inaturalist import (
    OBSERVATION_DISPLAY_COLUMNS,
    convert_to_geodataframe,
    split_observations_by_taxon,
    summarize_species
)

from src.streamlit_ui import (
    reset_selection,
    reset_search,
    display_trails_dataframe,
    display_species_groups,
    display_metrics,
)

# ==================================================
# Constants
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_PATH_TRAILS = PROCESSED_DIR / "dnr_up_hiking_trails_grouped.parquet"
PROCESSED_PATH_OBS = PROCESSED_DIR / "inaturalist_up_fall_observations.parquet"

STATIC_DIR = PROJECT_ROOT / "static"
MAP_IMAGE_PATH = STATIC_DIR / "map_up.jpg"
BANNER_PATH = STATIC_DIR / "banner.png"

VALID_SEARCH_RADII = [10, 25, 50]

TITLE = "What's UP Outdoors"

st.set_page_config(
    page_title = TITLE, 
    initial_sidebar_state = "expanded", 
    layout="wide"
)

# ==================================================
# Load Data
# ==================================================
@st.cache_data
def load_trails(): 
    return gpd.read_parquet(PROCESSED_PATH_TRAILS)

trails = load_trails()

@st.cache_data
def load_historical_observations():
    return pd.read_parquet(PROCESSED_PATH_OBS)

historical_observations = load_historical_observations()
historical_observations = convert_to_geodataframe(historical_observations)

# ==================================================
# Session States
# ==================================================
if "selected_rows" not in st.session_state:
    st.session_state.selected_rows = []

if "selected_trail" not in st.session_state:
    st.session_state.selected_trail = None

if "search_version" not in st.session_state:
    st.session_state.search_version = 0

length_categories = []
trail_name = ""
surface_type = ""


# ==================================================
# Side Bar
# ==================================================
st.sidebar.title("Find Trails Near You")

st.sidebar.write(
    "Enter a ZIP code and choose a search radius to find nearby Upper Peninsula trails."
)

st.sidebar.caption(
    "Search within 10, 25, or 50 miles of the selected ZIP code."
)

st.sidebar.image(MAP_IMAGE_PATH)


# ==================================================
# ZIP Code Search
# ==================================================
zipcode = st.sidebar.text_input(
    "Enter UP Zipcode: ",
    key="zipcode",
    on_change=reset_selection
)

radius = st.sidebar.radio(
    "Search Radius (Miles): ", 
    VALID_SEARCH_RADII, 
    horizontal = True,
    on_change=reset_selection
)

trails_to_display = trails.copy()

if zipcode: 
    try:
        zip_info = get_zip_info(zipcode)

        st.sidebar.markdown(
            f"""
        **ZIP:** {zip_info["zipcode"]}  
        **City:** {zip_info["place"]}  
        **County:** {zip_info["county"]}  
        **State:** {zip_info["state"]}
        """
        )     

        zip_point = zip_to_point(zipcode)
    
        trails_to_display = find_nearby_trails(
            trails, 
            zip_point, 
            radius
        )

        trails_to_display["DistanceToTrailMiles"] = distance_to_trails(
            trails_to_display, 
            zip_point
        )


    except ValueError as exc:
        st.sidebar.error(str(exc))


# ==================================================
# Main Page with Tabs
# ==================================================
st.header(f"{TITLE}: Upper Peninsula Trail Explorer")
st.image(BANNER_PATH)

st.subheader(f"How to use {TITLE}: ")

st.write(
    "Browse trails across Michigan’s Upper Peninsula, narrow the list by length "
    "or trail name, and select a trail to see more details and nearby iNaturalist "
    "observations. Looking for trails near you? Use the ZIP code search in the sidebar."
)

st.divider()

col1, col2, col3, col4 = st.columns([0.75,1.5,1,2])

with col1:
    button_label = (
        "ZIP Search in sidebar"
        if zipcode == ""
        else "Reset ZIP code"
    )

    st.button(
        button_label,
        on_click=reset_search,
        disabled=zipcode == ""
    )

with col2:
    length_categories = st.multiselect(
        "Length Category",
        options=["Short", "Medium", "Long", "Extremely Long"],
        on_change=reset_selection
    )
            
with col3:
    surface_type = st.text_input(
        "Surface Type",
        placeholder="Search by surface type",
        on_change=reset_selection
    )

with col4:
    trail_name = st.text_input(
        "Trail Name",
        placeholder="Search by trail name",
        on_change=reset_selection
    )

filtered_trails = filter_trails(
    trails_to_display,
    length_categories,
    trail_name,
    surface_type
)

st.divider()

# ==================================================
# Tabs
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    ":hiking_boot: **Browse & Filter Trails**",
    ":round_pushpin: **Explore Trails on Map**",
    ":eagle: **Selected Trail Details**",
    ":star: **Saved Favorite Trails**",
])

# ==================================================
# Tab 1: Trails table
# ==================================================
with tab1:
    
    if filtered_trails.empty:
        st.info("No trails match the current filters.")

    else: 
        event = display_trails_dataframe(filtered_trails, selectable=True)

        st.session_state.selected_rows = event.selection.rows

        st.divider()
        display_metrics(filtered_trails)

# ==================================================
# Tab 2: Map
# ==================================================
with tab2: 
    trail_map = build_trail_map(filtered_trails, zipcode)
    st_folium(trail_map, height=600, width=1000)

    st.divider()

    display_metrics(filtered_trails)

# ==================================================
# Tab 3: Specific Trail details
# ==================================================
with tab3:
    if st.session_state.selected_rows:
        row_idx = st.session_state.selected_rows[0]
        selected_trail = filtered_trails.iloc[[row_idx]]

        st.subheader(
            f'Trail: {selected_trail["HikingName"].iloc[0]} '
            f'in {selected_trail["County"].iloc[0]} County'
        )

        display_trails_dataframe(
            selected_trail,
            selectable=False
        )
           
        st.header(
            "iNaturalist Historical Observations Sept-Oct 2015-2025"
        )
        
        filtered_historical_observations = (
            filter_observations_near_trail(
                selected_trail, 
                historical_observations
            )
        )

        display_species_groups(
            filtered_historical_observations
        )

    else:
        st.info(
            "Click on a trail in tab 1 to see details."
        )

# ==================================================
# Tab 4: Favorite Trails
# ==================================================
with tab4:
    st.write("Favorites Coming Soon")