"""Defines the Streamlit user interface for What's UP Outdoors."""

from pathlib import Path

import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd 
import pandas as pd
import requests


from src.trails import (
    filter_trails,
    favorite_trails_df
)

from src.locations import (
    zip_to_point,
    get_zip_info
)
from src.spatial import (
    find_nearby_trails, 
    distance_to_trails,
    create_trail_buffer,
    filter_observations_near_trail,
    add_taxon_density_to_trails
)
from src.maps import (
    build_trail_map,
    display_observation_map_fragment
)
from src.inaturalist import (
    convert_to_geodataframe,
    normalize_recent_observations,
    limit_observations
)
from src.apis.inaturalist_api import (
    DAYS_RETRIEVED,
    fetch_recent_observations
)
from src.streamlit_ui import (
    reset_selection,
    reset_search,
    display_trails_dataframe,
    display_favorite_trails_dataframe,
    display_species_groups,
    display_metrics,
    favorite_button_display,
    select_favorite_for_details,
    display_favorites_map,
    remove_favorite,
    add_notes_button,
    download_button,
)
from src.ai import (
    build_trail_ai_data,
    describe_trail,
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
    layout="wide"
)

# ==================================================
# Load Data
# ==================================================
@st.cache_data(show_spinner="Loading trail data...", show_time=True)
def load_trails(): 
    return gpd.read_parquet(PROCESSED_PATH_TRAILS)

trails = load_trails()

@st.cache_data(show_spinner="Loading historical iNaturalist observations...", show_time=True)
def load_historical_observations():
    observations = pd.read_parquet(PROCESSED_PATH_OBS)
    
    return convert_to_geodataframe(observations)

historical_observations = load_historical_observations()

@st.cache_data(show_spinner="Preparing trail and historical observation data...", show_time=True)
def add_historical_taxon_counts(_trails, _historical_observations):
    return add_taxon_density_to_trails(_trails, _historical_observations)

trails = add_historical_taxon_counts(trails, historical_observations)

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

if "favorites_notes" not in st.session_state:
    st.session_state.favorites_notes = {}

if "favorite_selection_version" not in st.session_state:
    st.session_state.favorite_selection_version = 0

if "favorites_ai_summaries" not in st.session_state:
    st.session_state.favorites_ai_summaries = {}

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
    "Browse hiking trails across Michigan’s Upper Peninsula, narrow the results "
    "with trail filters or a ZIP code search, and select a trail to explore detailed "
    "trail information and nearby iNaturalist observations. Use the tabs below to "
    "compare trails, explore them on a map, view a selected trail, and manage your "
    "saved favorites and trail notes."
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
        options=["Short < 2mi", "Medium 2-7mi", "Long 7-20mi", "Extremely Long 20mi+"],
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    ":hiking_boot: **Browse & Filter Trails**",
    ":round_pushpin: **Explore Trails Map**",
    ":eagle: **Trail Observations Details**",
    ":sparkles: **AI Trail Summary**",
    ":star: **Saved Favorite Trails**",
])

# ==================================================
# Tab 1: Trails table
# ==================================================
with tab1:
    st.header("Browse & Filter Trails")

    st.markdown(
        "Compare trails that match your current search and filters. Select a trail "
        "from the table, then open the Selected Trail Details tab to view trail "
        "information and nearby iNaturalist observations."
    )


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
    st.header("Explore Trails on Map")

    st.markdown(
        "View the trails that match your current search and filters on an "
        "interactive map. Hover over a trail for its name and county, or click "
        "it to view additional trail information."
    )

    with st.spinner("Loading trail map...", show_time=True):
        trail_map = build_trail_map(
            filtered_trails,
            zip_point
        )

        st_folium(
            trail_map,
            height=600,
            width=1000,
            returned_objects=[] # Prevent map interactions from triggering Streamlit reruns
        )

    st.divider()


    display_metrics(filtered_trails)
    st.caption(
        "Summary metrics reflect the trails currently displayed on the map."
    )

# ==================================================
# Tab 3: Specific Trail details
# ==================================================
with tab3:
    if selected_trail is not None:

        st.header("Selected Trail Details")
        st.subheader("iNaturalist Observations")

        trail_name = selected_trail["HikingName"].iloc[0]

        st.markdown(
            "Explore iNaturalist observations reported within "
            f"two miles of **{trail_name}**. "
            f"**Recent observations** cover the previous {DAYS_RETRIEVED} days, while "
            "**historical observations** cover September–October from 2015–2025. "
            "Use the map filter to view all supported taxon groups or focus on a single group. "
            "Recent observations are retrieved the first time a trail is selected, so the "
            "initial load may take longer than repeat views during the current session. "
            "[Learn more about iNaturalist](https://www.inaturalist.org/)."
        )
        st.subheader(
            f'Trail: {selected_trail["HikingName"].iloc[0]} '
            f'in {selected_trail["County"].iloc[0]} County'
        )

        fav_col, trail_col = st.columns([1,7])
        with fav_col:
            favorite_button_display(st.session_state.selected_trail_id)

        with trail_col:
            display_trails_dataframe(
                selected_trail,
                selectable=False
            )

# ==================================================
# iNaturalist API and Historical data
# ==================================================
        buffer = create_trail_buffer(selected_trail)
        api_warning = "Recent observations unavailable."
        filtered_api_observations = pd.DataFrame()
        
        with st.spinner("Loading recent observations...", show_time=True):
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


            except requests.exceptions.RequestException:
                st.warning(api_warning)


            filtered_historical_observations = (
                filter_observations_near_trail(
                    selected_trail, 
                    historical_observations
                )
            )
        if not filtered_api_observations.empty:
            limited_api_observations = limit_observations(filtered_api_observations)
        else:
            limited_api_observations = filtered_api_observations

        limited_hist_observations = limit_observations(filtered_historical_observations)

        display_observation_map_fragment(
            selected_trail, 
            limited_api_observations,
            limited_hist_observations, 
            filtered_historical_observations
        )
        
        recent_col, historical_col = st.columns(2)

        with recent_col:
            st.subheader(
                f"Recent Observations: Last {DAYS_RETRIEVED} Days"
            )
            display_species_groups(
                limited_api_observations
            )
        with historical_col: 
            st.subheader(
                "Historical Observations: Sept-Oct 2015-2025"
            )

            display_species_groups(
                limited_hist_observations
            )

    else:
        st.info(
            "Select a trail from Browse & Filter Trails or choose a saved favorite "
            "to view its details."
        )

# ==================================================
# Tab 4: AI Trail Summary
# ==================================================
with tab4:
    st.header("AI Trail Summary")

    st.markdown(
        """
        Generate an AI overview of the selected trail using its trail details,
        recent iNaturalist observations, and historical observation patterns.
        Overviews are saved for downloaded favorites.
        """
    )

    if selected_trail is None:
        st.info(
            "Click on a trail in tab 1 to see details."
        )
    
    else:
        trail_data = build_trail_ai_data(selected_trail, limited_api_observations)
        
        if  st.button("Generate AI Overview"):
            summary = describe_trail(trail_data)

            st.session_state.favorites_ai_summaries[
                st.session_state.selected_trail_id
            ] = summary

        saved_summary = st.session_state.favorites_ai_summaries.get(
            st.session_state.selected_trail_id
        )

        if saved_summary:
            st.subheader(f"AI Overview for {st.session_state.selected_trail_id}")
            st.write(saved_summary)

# ==================================================
# Tab 5: Favorite Trails
# ==================================================
with tab5:
    st.header("Saved Favorite Trails")

    st.markdown(
        "View and manage your saved favorite trails. Select a trail to view details, "
        "remove it from your favorites, or add personal notes. Notes and AI summaries "
        "are saved for the current session and included in the favorites CSV download."
    )

    favorites_df = favorite_trails_df(
        trails, 
        st.session_state.favorites
    )

    display_favorites_map(trails)

    
    selected_favorite = display_favorite_trails_dataframe(
        favorites_df
    )

    notes_col, manage_col = st.columns(2)

    with notes_col:
        select_favorite_for_details(selected_favorite)
        add_notes_button(trails, selected_favorite)

    with manage_col:
        remove_favorite(selected_favorite)  
        download_button(trails)

    with st.expander("View All Notes"):
        if st.session_state.favorites_notes.items():
            for trail_id, note in st.session_state.favorites_notes.items():
                st.subheader(trail_id)
                st.write(note)
        else:
            st.info("No trail notes saved yet.")

    with st.expander("View All AI Summaries"):
        if st.session_state.favorites_ai_summaries.items():
            for trail_id, overview in st.session_state.favorites_ai_summaries.items():
                st.subheader(trail_id)
                st.write(overview)

st.divider()

st.caption(
    "Originally built while planning a fall-color trip through Michigan’s Upper Peninsula. "
    "What’s UP Outdoors combines trail information with nearby nature observations to help "
    "explore possible hiking destinations."
)

st.markdown(
    "Built by [Ray Hobbs](https://github.com/RayofData/This-is-Ray-of-Data) · "
    "[GitHub](https://github.com/RayofData/Whats_UP_Outdoors) · "
    "[LinkedIn](https://www.linkedin.com/in/ray-hobbs/)"
)