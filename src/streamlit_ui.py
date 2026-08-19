"""Streamlit UI helpers for application state, trail tables, metrics, and species displays."""

import pandas as pd
import streamlit as st

from src.inaturalist import (
    split_observations_by_taxon,
    summarize_species,
)

from src.trails import (
    favorite_trails_df
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
    
    st.dataframe(
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
    )

    return display_df


@st.fragment
def display_favorites_section(trails):
    """Display and refresh favorite trails and session notes."""

    favorites_df = favorite_trails_df(
        trails,
        st.session_state.favorites
    )

    display_df = display_favorite_trails_dataframe(
        favorites_df
    )

    st.button(
        "Refresh Favorites",
        key = "refresh_favorites"
    )

    if display_df.empty:
        st.info("No favorite trails saved yet.")
        return

    st.subheader("Trail Notes")

    for _, trail in display_df.iterrows():
        trail_id = trail["TrailGroupName"]

        note = st.text_area(
            trail["HikingName"],
            value = st.session_state.favorites_notes.get(
                trail_id,
                ""
            ),
            key = f"favorite_note_{trail_id}",
            placeholder = f"Add notes about {trail['HikingName']}"
        )

        st.session_state.favorites_notes[trail_id] = note


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


@st.fragment
def favorite_button_display(trail_id):
    is_favorite = (
        trail_id
        in st.session_state.favorites
    )

    if is_favorite:
        if st.button("Remove Favorite"):
            st.session_state.favorites.remove(trail_id)
            st.rerun(scope="fragment")
    
    else:
        if st.button("Add Favorite"):
            st.session_state.favorites.append(trail_id)
            st.rerun(scope="fragment")