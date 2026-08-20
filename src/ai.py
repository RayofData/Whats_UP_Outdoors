"""Build and cache AI-generate trail information."""

import json

import streamlit as st

from apis.genai_api import (
    generate_text
)



@st.cache_data(ttl="1d", max_entries=500)
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

        
north_trail_data = {
    "trail": {
        "name": "North Country Trail",
        "county": "Alger",
        "length_miles": 96.9903,
        "width": "Varies",
        "surface": "Concrete, Dirt Natural",
    },

    "recent_observations": {
        "period_days": 21,
        "species_limit": 10,
        "observation_limit": 40,

        "Birds": {
            "observation_count": 16,
            "species": [
                {"name": "Mallard", "count": 3, "most_recent": "2026-08-13"},
                {"name": "Calidris Sandpipers", "count": 2, "most_recent": "2026-08-14"},
                {"name": "Ducks, Geese, and Swans", "count": 2, "most_recent": "2026-08-13"},
                {"name": "Common Merganser", "count": 2, "most_recent": "2026-08-10"},
                {"name": "Wild Turkey", "count": 1, "most_recent": "2026-08-19"},
                {"name": "Bald Eagle", "count": 1, "most_recent": "2026-08-13"},
                {"name": "Sandpipers and Allies", "count": 1, "most_recent": "2026-08-13"},
                {"name": "Ring-billed Gull", "count": 1, "most_recent": "2026-08-12"},
                {"name": "Stilt Sandpiper", "count": 1, "most_recent": "2026-08-11"},
                {"name": "Semipalmated Plover", "count": 1, "most_recent": "2026-08-11"},
            ],
        },

        "Mammals": {
            "observation_count": 4,
            "species": [
                {"name": "Eastern Chipmunk", "count": 1, "most_recent": "2026-08-17"},
                {"name": "White-tailed Deer", "count": 1, "most_recent": "2026-08-13"},
                {"name": "American Black Bear", "count": 1, "most_recent": "2026-08-13"},
                {"name": "American Beaver", "count": 1, "most_recent": "2026-08-09"},
            ],
        },

        "Plants": {
            "observation_count": 40,
            "species": [
                {"name": "lesser burdock", "count": 2, "most_recent": "2026-08-19"},
                {"name": "Broad-leaved helleborine", "count": 2, "most_recent": "2026-08-19"},
                {"name": "star-flowered lily-of-the-valley", "count": 2, "most_recent": "2026-08-18"},
                {"name": "bluebead lily", "count": 2, "most_recent": "2026-08-17"},
                {"name": "common selfheal", "count": 2, "most_recent": "2026-08-17"},
                {"name": "rock polypody", "count": 2, "most_recent": "2026-08-16"},
                {"name": "goldenrods", "count": 2, "most_recent": "2026-08-16"},
                {"name": "grey alder", "count": 1, "most_recent": "2026-08-18"},
                {"name": "common milkweed", "count": 1, "most_recent": "2026-08-18"},
                {"name": "green ash", "count": 1, "most_recent": "2026-08-18"},
            ],
        },

        "Fungi": {
            "observation_count": 40,
            "species": [
                {"name": "Fungi Including Lichens", "count": 4, "most_recent": "2026-08-16"},
                {"name": "amanita mushrooms", "count": 2, "most_recent": "2026-08-16"},
                {"name": "Brittle Cinder", "count": 2, "most_recent": "2026-08-16"},
                {"name": "brittlegills", "count": 2, "most_recent": "2026-08-16"},
                {"name": "Dacrymyces", "count": 2, "most_recent": "2026-08-13"},
                {"name": "gray reindeer lichen", "count": 2, "most_recent": "2026-08-09"},
                {"name": "Netted shield lichen", "count": 2, "most_recent": "2026-08-09"},
                {"name": "Phaeolus hispidoides", "count": 1, "most_recent": "2026-08-17"},
                {"name": "Northern Tooth", "count": 1, "most_recent": "2026-08-16"},
                {"name": "Daldinia", "count": 1, "most_recent": "2026-08-16"},
            ],
        },

        "Reptiles": {
            "observation_count": 4,
            "species": [
                {"name": "Red-bellied Snake", "count": 1, "most_recent": "2026-08-13"},
                {"name": "Common Garter Snake", "count": 1, "most_recent": "2026-08-13"},
                {"name": "Common Snapping Turtle", "count": 1, "most_recent": "2026-08-12"},
                {"name": "Painted Turtle", "count": 1, "most_recent": "2026-08-12"},
            ],
        },

        "Insects": {
            "observation_count": 40,
            "species": [
                {"name": "Nymphalis l-album j-album", "count": 3, "most_recent": "2026-08-17"},
                {"name": "White Underwing", "count": 2, "most_recent": "2026-08-19"},
                {"name": "Lesser Maple Spanworm Moth", "count": 2, "most_recent": "2026-08-16"},
                {"name": "Great Spangled Fritillary", "count": 2, "most_recent": "2026-08-13"},
                {"name": "lobed mason wasp", "count": 2, "most_recent": "2026-08-09"},
                {"name": "Tricolored Bumble Bee", "count": 2, "most_recent": "2026-08-09"},
                {"name": "Yellow-banded Bumble Bee", "count": 2, "most_recent": "2026-08-09"},
                {"name": "White-faced Meadowhawk", "count": 2, "most_recent": "2026-08-09"},
                {"name": "Narrow-headed Marsh Fly", "count": 1, "most_recent": "2026-08-18"},
                {"name": "Boarmiini", "count": 1, "most_recent": "2026-08-16"},
            ],
        },
    },

    "historical_observation_density": {
        "Birds": 0.44,
        "Mammals": 0.19,
        "Plants": 10.73,
        "Fungi": 2.95,
        "Reptiles": 0.03,
        "Insects": 0.59,
        "unit": "observations per square mile",
    },
}


fox_trail_data = {
    "trail": {
        "name": "Fox River Pathway",
        "county": "Alger",
        "length_category": "Long",
        "length_miles": 14.3451,
        "width": "0 To 2 Feet",
        "surface": "Dirt Natural",
        "status": "Open",
    },

    "recent_observations": {
        "period_days": 21,
        "species_limit": 10,
        "observation_limit": 40,

        "Birds": {
            "observation_count": 0,
            "species": [],
        },

        "Mammals": {
            "observation_count": 0,
            "species": [],
        },

        "Plants": {
            "observation_count": 8,
            "species": [
                {
                    "name": "red pine",
                    "count": 2,
                    "most_recent": "2026-08-09",
                },
                {
                    "name": "eastern white pine",
                    "count": 2,
                    "most_recent": "2026-08-09",
                },
                {
                    "name": "Ram's-head Lady's Slipper",
                    "count": 1,
                    "most_recent": "2026-08-13",
                },
                {
                    "name": "common jewelweed",
                    "count": 1,
                    "most_recent": "2026-08-12",
                },
                {
                    "name": "Jack pine",
                    "count": 1,
                    "most_recent": "2026-08-09",
                },
                {
                    "name": "quaking aspen",
                    "count": 1,
                    "most_recent": "2026-08-09",
                },
            ],
        },

        "Fungi": {
            "observation_count": 1,
            "species": [
                {
                    "name": "Fly Agaric",
                    "count": 1,
                    "most_recent": "2026-08-12",
                },
            ],
        },

        "Reptiles": {
            "observation_count": 0,
            "species": [],
        },

        "Insects": {
            "observation_count": 1,
            "species": [
                {
                    "name": "American Carrion Beetle",
                    "count": 1,
                    "most_recent": "2026-08-03",
                },
            ],
        },
    },

    "historical_observation_density": {
        "Birds": 0.05,
        "Mammals": 0.03,
        "Plants": 1.03,
        "Fungi": 0.67,
        "Reptiles": 0.0,
        "Insects": 0.07,
        "unit": "observations per square mile",
    },
}

iron_belle_trail_data = {
    "trail": {
        "name": "Iron Belle Trail",
        "county": "Schoolcraft",
        "length_category": "Extremely Long",
        "length_miles": 38.0915,
        "width": "0 To 2 Feet",
        "surface": "Asphalt",
        "status": "Open",
    },

    "recent_observations": {
        "period_days": 21,
        "species_limit": 10,
        "observation_limit": 40,

        "Birds": {
            "observation_count": 1,
            "species": [
                {
                    "name": "Northern Waterthrush",
                    "count": 1,
                    "most_recent": "2026-08-02",
                },
            ],
        },

        "Mammals": {
            "observation_count": 0,
            "species": [],
        },

        "Plants": {
            "observation_count": 23,
            "species": [
                {
                    "name": "American searocket",
                    "count": 2,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "star-flowered lily-of-the-valley",
                    "count": 2,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "common yarrow",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "red baneberry",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "purple false foxglove",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "Beach Wormwood",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "American marram grass",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "spotted knapweed",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "Pitcher's thistle",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "red osier dogwood",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
            ],
        },

        "Fungi": {
            "observation_count": 1,
            "species": [
                {
                    "name": "Elegant Sunburst Lichen",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
            ],
        },

        "Reptiles": {
            "observation_count": 1,
            "species": [
                {
                    "name": "Smooth Greensnake",
                    "count": 1,
                    "most_recent": "2026-08-04",
                },
            ],
        },

        "Insects": {
            "observation_count": 13,
            "species": [
                {
                    "name": "Spider Wasps",
                    "count": 3,
                    "most_recent": "2026-08-09",
                },
                {
                    "name": "Pine tree Spur-throat Grasshopper",
                    "count": 1,
                    "most_recent": "2026-08-15",
                },
                {
                    "name": "Nymphalis l-album j-album",
                    "count": 1,
                    "most_recent": "2026-08-14",
                },
                {
                    "name": "Anoplius",
                    "count": 1,
                    "most_recent": "2026-08-09",
                },
                {
                    "name": "Cimbex",
                    "count": 1,
                    "most_recent": "2026-08-09",
                },
                {
                    "name": "Monarch",
                    "count": 1,
                    "most_recent": "2026-08-07",
                },
                {
                    "name": "Picromerus",
                    "count": 1,
                    "most_recent": "2026-08-07",
                },
                {
                    "name": "Five-spotted Spider Wasp",
                    "count": 1,
                    "most_recent": "2026-08-06",
                },
                {
                    "name": "Giant Mayfly",
                    "count": 1,
                    "most_recent": "2026-08-03",
                },
                {
                    "name": "Fall Webworm Moth",
                    "count": 1,
                    "most_recent": None,
                },
            ],
        },
    },

    "historical_observation_density": {
        "Birds": 0.08,
        "Mammals": 0.04,
        "Plants": 1.45,
        "Fungi": 0.37,
        "Reptiles": 0.04,
        "Insects": 0.43,
        "unit": "observations per square mile",
    },
}

if st.button("Generate Text North Trail"):
    summary=describe_trail(north_trail_data)
    st.write(summary)

if st.button("Generate Text Fox Trail"):
    summary=describe_trail(fox_trail_data)
    st.write(summary)

if st.button("Generate Text Iron Trail"):
    summary=describe_trail(iron_belle_trail_data)
    st.write(summary)