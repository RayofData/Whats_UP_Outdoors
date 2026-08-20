"""Streamlit UI helpers for application state, trail tables, metrics, and species displays."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from datetime import datetime

from src.inaturalist import (
    split_observations_by_taxon,
    summarize_species,
)

from src.trails import (
    favorite_trails_df
)

from src.maps import (
    build_trail_map
)

def reset_selection():
    """Clear the selected trail when search criteria change."""
    st.session_state.selected_trail_id = None

    current_version = st.session_state.get("search_version", 0)

    if not isinstance(current_version, int):
        current_version = 0

    st.session_state.search_version = current_version + 1


def reset_search():
    """Resets zip to reset table"""
    st.session_state.zipcode = ""
    reset_selection() 
    
     
def display_trails_dataframe(trails, selectable=False):
    """Display trail data with readable Streamlit column formatting."""
    display_df = pd.DataFrame(
        trails.drop(columns="geometry", errors="ignore")
    )

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
            "BirdsPerSqMile",
            "MammalsPerSqMile",
            "PlantsPerSqMile",
            "FungiPerSqMile",
            "ReptilesPerSqMile",
            "InsectsPerSqMile",
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
            "key": f"selection_{st.session_state.search_version}",
        })

    return st.dataframe(
        display_df,
        **dataframe_options,
    )


def add_taxon_density_display_column(trails):
    """Add a formatted taxon-density summary column."""
    display_df = trails.copy()

    display_df["TaxonDensity"] = (
        display_df.apply(
            lambda row: (
                f"Birds: {row['BirdsPerSqMile']:.1f}"
                f" | Mammals: {row['MammalsPerSqMile']:.1f}"
                f" | Plants: {row['PlantsPerSqMile']:.1f}"
                f" | Fungi: {row['FungiPerSqMile']:.1f}"
                f" | Reptiles: {row['ReptilesPerSqMile']:.1f}"
                f" | Insects: {row['InsectsPerSqMile']:.1f}"
            ),
            axis=1,
        )
    )

    return display_df


def display_favorite_trails_dataframe(trails):
    """Display favorite trail data with taxon density."""
    display_df = pd.DataFrame(
        trails.drop(columns="geometry", errors="ignore")
    )

    display_df = add_taxon_density_display_column(display_df)

    event = st.dataframe(
        display_df,
        column_order = [
            "HikingName",
            "County",
            "LengthCategory",
            "ReportedLengthMiles",
            "TrailWidth",
            "SurfaceTypes",
            "TaxonDensity",
        ],
        column_config = {
            "HikingName": "Trail",
            "County": "County",
            "LengthCategory": "Length Category",
            "ReportedLengthMiles": "Length (Miles)",
            "TrailWidth": "Width",
            "SurfaceTypes": "Surface",
            "TaxonDensity": "Taxon Density",
        },
        hide_index = True,
        on_select = "rerun",
        selection_mode = "single-row",
        key = f"favorite_trail_selection_{st.session_state.favorite_selection_version}",
        )

    if event.selection.rows:
        row_idx = event.selection.rows[0]

        return display_df.iloc[row_idx]["TrailGroupName"]

    if display_df.empty:
        st.info("No favorite trails saved yet.")

    return None


def display_favorites_map(trails):
    """Display favorite trails on map with download button."""

    favorites_df = favorite_trails_df(
        trails,
        st.session_state.favorites
    )

    with st.spinner("Loading trail map...", show_time=True):
        favorites_map = build_trail_map(favorites_df)

        st_folium(
            favorites_map,
            height=600,
            width=1000,
            returned_objects=[] # Prevent map interactions from triggering Streamlit reruns
        )

        map_html = favorites_map.get_root().render()

    st.download_button(
        label = "Download Trail Map",
        data = map_html,
        file_name = "trail_map.html",
        mime = "text/html"
    )


def remove_favorite(trail_id):
    """Button to remove selected trail from favorites."""
    if st.button("Remove Selected Favorite", disabled=trail_id is None):
        st.session_state.favorites.remove(trail_id)
        st.session_state.favorite_selection_version += 1
        st.rerun()


@st.dialog("Trail Note")
def trail_note_dialog(trails, trail_id):
    """Display a note editor for the selected favorite trail."""

    trail = trails.loc[trails["TrailGroupName"] == trail_id].iloc[0]

    note = st.text_area(
        f"Notes for {trail_id}",
        value = st.session_state.favorites_notes.get(
            trail_id,
            ""
        ),
        key = f"favorite_note_{trail_id}",
        placeholder = f"Add notes about {trail_id}"
    )

    if st.button("Save Note"):
        st.session_state.favorites_notes[trail_id] = note
        st.rerun()


def add_notes_button(trails, trail_id):
    """Open the note dialog for the selected favorite trail."""

    if st.button(
        "Add/Edit Trail Note",
        disabled=trail_id is None
    ):
        trail_note_dialog(trails, trail_id)


def download_button(trails):
    """Converts favorites into a dataframe with notes and download as csv."""
    favorites_df = favorite_trails_df(
        trails,
        st.session_state.favorites
    )

    download_df = add_taxon_density_display_column(
        favorites_df.drop(
            columns="geometry",
            errors="ignore"
        )
    )
    
    download_df["Notes"] = (
        download_df["TrailGroupName"]
        .map(st.session_state.favorites_notes)
        .fillna("")
    )


    download_df = download_df[
        [
            "HikingName",
            "County",
            "LengthCategory",
            "ReportedLengthMiles",
            "TrailWidth",
            "SurfaceTypes",
            "TaxonDensity",
            "Notes",
        ]
    ].rename(
        columns={
            "HikingName": "Trail",
            "ReportedLengthMiles": "Length (Miles)",
            "TrailWidth": "Width",
            "SurfaceTypes": "Surface",
            "TaxonDensity": "Taxon Density",
        }
    )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")

    filename = f"trail_favorites_{timestamp}.csv"
    
    st.download_button(
        label = "Download Favorites",
        data = download_df.to_csv(index = False),
        file_name=filename,
        mime="text/csv"
    )




def display_species_groups(observations):
    """Display top species within each supported taxon group."""
    taxon_groups = split_observations_by_taxon(observations)

    for group_name, group_df in taxon_groups.items():  
        st.subheader(f"{group_name} — {len(group_df):,} observations")

        if group_df.empty:
            st.write(f"No observations found for {group_name}")
            continue
    
        top_species = summarize_species(group_df)

        image_col, count_col, species_col, date_col = st.columns(
            [1,1,3,2]
        )
        
        image_col.write("**Image**")
        count_col.write("**Count**")
        species_col.write("**Species**")
        date_col.write("**Most Recent**")

        for _, row in top_species.iterrows():
            image_col, count_col, species_col, date_col = st.columns(
                [1,1,3,2]
            )            
            with image_col:
                if pd.notna(row["image_url"]) and row["image_url"]:
                    st.image(
                        row["image_url"],
                        width=150
                    )
                else:
                    st.write("**No Image**")
            with count_col:
                st.write(str(row["observed_count"]))
            
            with species_col:
                st.write(row["common_name"])

            with date_col:
                st.write(row["most_recent"].strftime("%Y-%m-%d"))


def display_metrics(trails):
    """Display summary metrics for the currently displayed trails."""
    st.subheader("Metrics")
    total_col, short_col, med_col, long_col, xlong_col, miles_col = st.columns(6)

    with total_col:
        st.metric(
            label="Total Trails", 
            value=len(trails)
        )    
    
    with short_col:
        st.metric(
            label="Short Trails", 
            value=len(trails[trails["LengthCategory"]=="Short"])
        )  

    with med_col:
        st.metric(
            label="Medium Trails", 
            value=len(trails[trails["LengthCategory"]=="Medium"])
        ) 

    with long_col:
        st.metric(
            label="Long Trails", 
            value=len(trails[trails["LengthCategory"]=="Long"])
        ) 

    with xlong_col:
        st.metric(
            label="Extremely Long Trails", 
            value=len(trails[trails["LengthCategory"]=="Extremely Long"])
        )   

    with miles_col:
        st.metric(
            label="Total Miles", 
            value=trails["ReportedLengthMiles"].sum().round(2))


def favorite_button_display(trail_id):
    is_favorite = (
        trail_id
        in st.session_state.favorites
    )

    if is_favorite:
        if st.button("Remove Favorite"):
            st.session_state.favorites.remove(trail_id)
            st.rerun()
    
    else:
        if st.button("Add Favorite"):
            st.session_state.favorites.append(trail_id)
            st.rerun()