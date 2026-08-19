"""Streamlit UI helpers for application state, trail tables, metrics, and species displays."""

import pandas as pd
import streamlit as st

from src.inaturalist import (
    split_observations_by_taxon,
    summarize_species,
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

def display_favorite_trails_dataframe(trails):
    """Display favorite trail data with an editable notes column."""
    display_df = pd.DataFrame(
        trails.drop(columns="geometry", errors="ignore")
    )

    display_df["TaxonDensity"] = (
        "Birds: " + display_df["BirdsPerSqMile"].map("{:.2f}".format)
        + " | Mammals: " + display_df["MammalsPerSqMile"].map("{:.2f}".format)
        + " | Plants: " + display_df["PlantsPerSqMile"].map("{:.2f}".format)
        + " | Fungi: " + display_df["FungiPerSqMile"].map("{:.2f}".format)
        + " | Reptiles: " + display_df["ReptilesPerSqMile"].map("{:.2f}".format)
        + " | Insects: " + display_df["InsectsPerSqMile"].map("{:.2f}".format)
    )

    display_df["Notes"] = ""

    dataframe_options = {
        "column_order": [
            "HikingName",
            "County",
            "LengthCategory",
            "ReportedLengthMiles",
            "TrailWidth",
            "SurfaceTypes",
            "TaxonDensity",
            "Notes"
        ],
        "column_config": {
            "HikingName": "Trail",
            "County": "County",
            "LengthCategory": "Length Category",
            "ReportedLengthMiles": "Length (Miles)",
            "TrailWidth": "Width",
            "SurfaceTypes": "Surface",
            "TaxonDensity": "Taxon Density",
            "Notes": st.column_config.TextColumn(
                "Notes",
                help="Add personal notes about this trail.",
                width="large",
            ),
        },
        "hide_index": True,
    }


    edited_df = st.data_editor(
        display_df,
        disabled=[
            col for col in display_df.columns
            if col != "Notes"
        ],
        **dataframe_options,
    )

    return edited_df


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
