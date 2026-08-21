"""Build and cache AI-generate trail information."""

import json

import streamlit as st
import pandas as pd 

from src.apis.genai_api import (
    generate_text
)

from src.inaturalist import TAXON_GROUPS, summarize_species

DENSITY_COLUMNS = {
    "Birds": "BirdsPerSqMile",
    "Mammals": "MammalsPerSqMile",
    "Plants": "PlantsPerSqMile",
    "Fungi": "FungiPerSqMile",
    "Reptiles": "ReptilesPerSqMile",
    "Insects": "InsectsPerSqMile",
}

def build_trail_ai_data(selected_trail, recent_observations):
    """Build structured trail data and recent-observation data for AI summaries."""
    trail = selected_trail.iloc[0]

    trail_data = {
        "trail": {
            "name": trail["HikingName"],
            "county": trail["County"],
            "length_miles": trail["ReportedLengthMiles"],
            "width": trail["TrailWidth"],
            "surface": trail["SurfaceTypes"],
        },
        "recent_observations": {
            "period_days": 21,
            "species_limit": 10,
            "observation_limit": 40,
        },
        "historical_observation_density": {
            group: trail[column]
            for group, column in DENSITY_COLUMNS.items()
        },
    }

    trail_data["historical_observation_density"]["unit"] = (
        "observations per square mile"
    )

    for group, iconic_taxon in TAXON_GROUPS.items():
        group_observations = recent_observations.loc[
            recent_observations["iconic_taxon"] == iconic_taxon
        ]

        species_summary = summarize_species(group_observations)

        species = []

        for _, row in species_summary.iterrows():
            species.append(
                {
                    "name": (
                        row["common_name"]
                        if pd.notna(row["common_name"])
                        else row["scientific_name"]
                    ),
                    "count": int(row["observed_count"])
                }
            )
        
        trail_data["recent_observations"][group] = {
            "observation_count": len(group_observations),
            "species": species
        }
    
    return trail_data


@st.cache_data(ttl="1d", max_entries=500, show_spinner=True, show_time=True)
def _generate_trail_summary(trail_data):
    """Return a natural-language summary of the supplied trail details."""
    prompt = f"""
    Write a short, natural hiking trail overview using only the supplied trail data.

    You may use general knowledge to interpret listed species, but do not invent
    species or trail facts. Treat iNaturalist observations as reported sightings
    near the trail, not guaranteed encounters.

    Highlight only a few notable species across the data, especially fall-color
    plants, interesting fungi and birds, and mammals that are notable or may
    warrant caution. Do not list every species.

    Trail data:
    {json.dumps(trail_data, indent=2)}
    """

    return generate_text(prompt)


def describe_trail(trail_data):
    """Return a trail summary or a fallback message if generation fails."""
    try:
        return _generate_trail_summary(trail_data)

    except Exception:
        return "AI summary unavailable."

