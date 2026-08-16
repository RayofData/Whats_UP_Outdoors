"""Defines the Streamlit user interface for What's UP Outdoors."""

from pathlib import Path

import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd 
import pandas as pd
import requests


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
    distances_to_trail,
    create_trail_buffer
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
    summarize_species,
    normalize_recent_observations
)
from src.apis.inaturalist_api import (
    fetch_recent_observations
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
PROCESSED_PATH_OBS = PROCESSED_DIR / "inaturalist_historical_up_fall_observations.parquet"

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
    observations = pd.read_parquet(PROCESSED_PATH_OBS)
    
    return convert_to_geodataframe(observations)

historical_observations = load_historical_observations()

# ==================================================
# Session States
# ==================================================
if "selected_trail_id" not in st.session_state:
    st.session_state.selected_trail_id = None

if "search_version" not in st.session_state:
    st.session_state.search_version = 0

if "recent_observations" not in st.session_state:
    st.session_state.recent_observations = {}

if "favorites" not in st.session_state:
    st.session_state.favorites = []


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
zip_point = None

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
st.title(f"{TITLE}: Upper Peninsula Trail Explorer")
st.image(BANNER_PATH)

st.subheader(f"How to use {TITLE}: ")

st.write(
    "Browse trails across Michigan’s Upper Peninsula, narrow the list by length "
    "or trail name, and select a trail to see more details and nearby iNaturalist "
    "observations. Looking for trails near you? Use the ZIP code search in the sidebar."
)

st.divider()

zip_col, len_col, surface_col, name_col = st.columns([0.75,1.5,1,2])

with zip_col:
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

with len_col:
    length_categories = st.multiselect(
        "Length Category",
        options=["Short", "Medium", "Long", "Extremely Long"],
        on_change=reset_selection
    )
            
with surface_col:
    surface_type = st.text_input(
        "Surface Type",
        placeholder="Search by surface type",
        on_change=reset_selection
    )

with name_col:
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
        event = display_trails_dataframe(
            filtered_trails, 
            selectable=True
        )

        if event.selection.rows:
            row_idx = event.selection.rows[0]
            
            st.session_state.selected_trail_id = (
                filtered_trails.iloc[row_idx]["TrailGroupName"]
            )

        st.divider()
        display_metrics(filtered_trails)

# ==================================================
# Resolve selected trail
# ==================================================
selected_trail = None

if st.session_state.selected_trail_id is not None:
    matches = trails.loc[
        trails["TrailGroupName"]
        == st.session_state.selected_trail_id
    ]
    
    if len(matches) == 1:
        selected_trail = matches.iloc[[0]]
    else: 
        st.session_state.selected_trail_id = None
    

# ==================================================
# Tab 2: Map
# ==================================================
with tab2: 
    trail_map = build_trail_map(
        filtered_trails,
        zip_point
    )

    st_folium(trail_map, height=600, width=1000)

    st.divider()

    display_metrics(filtered_trails)

# ==================================================
# Tab 3: Specific Trail details
# ==================================================
with tab3:
    if selected_trail is not None:

        st.subheader(
            f'Trail: {selected_trail["HikingName"].iloc[0]} '
            f'in {selected_trail["County"].iloc[0]} County'
        )

        display_trails_dataframe(
            selected_trail,
            selectable=False
        )

        buffer = create_trail_buffer(selected_trail)

        st.header("iNaturalist Observations")

        st.markdown(
            "Explore recent and historical sightings reported within two miles of the "
            "selected trail using data from [iNaturalist](https://www.inaturalist.org/), "
            "a community platform for recording and sharing observations of biodiversity."
        )

        recent_col, historical_col = st.columns(2)

        with recent_col:
            st.subheader(
                "Recent Observations: Last 21 Days"
            )
            api_warning = "Recent observations unavailable."
            try: 
                trail_id = st.session_state.selected_trail_id

                if trail_id not in st.session_state.recent_observations:

                    api_observations = fetch_recent_observations(buffer)
                    
                    normalized_observations = normalize_recent_observations(api_observations)

                    filtered_api_observations = filter_observations_near_trail(
                        selected_trail,
                        normalized_observations
                    )

                    st.session_state.recent_observations[
                        trail_id
                    ] = filtered_api_observations

                filtered_api_observations = st.session_state.recent_observations[trail_id]
                display_species_groups(
                    filtered_api_observations
                )

            except requests.exceptions.RequestException:
                st.warning(api_warning)
            except requests.exceptions.HTTPError: 
                st.warning(api_warning)
            except requests.exceptions.ConnectionError:
                st.warning(api_warning)
            except requests.ReadTimeout:
                st.warning(api_warning)
            

        with historical_col: 
            st.subheader(
                "Historical Observations: Sept-Oct 2015-2025"
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
