![What's UP Outdoors banner](static/banner.png)

# What’s UP Outdoors: Upper Peninsula Trail Explorer

What’s UP Outdoors is a Python and Streamlit portfolio project for discovering hiking trails and nearby iNaturalist observations in Michigan’s Upper Peninsula.

The MVP emphasizes reproducible geospatial processing, API integration, automated testing, and a maintainable modular structure.

## MVP Features

- Search from any valid United States ZIP code
- Choose a 10, 25, or 50 mile search radius
- View up to 20 nearby UP trails, ordered from nearest to farthest
- Compare trail name, county, length category, reported length, width, surface, status, and distance from the entered ZIP code
- Explore all trails or nearby search results on a Folium map
- Select any Upper Peninsula trail for a detailed trail view
- Map recent and historical iNaturalist observations within two miles of the selected trail
- View recent observations from the previous 21 days
- View fixed historical September–October observations from 2015–2025
- View up to 10 species within each supported taxon group
- Save favorite trails during the current Streamlit session
- Export favorites as a CSV file

## Application Layout

The Streamlit app uses three main tabs:

1. **Trails** — displays all trails before a ZIP search and up to 20 nearby trails after a search.
2. **Map** — displays the corresponding trail set on an interactive Folium map.
3. **Trail Details** — allows selection of any Upper Peninsula trail and displays trail attributes, nearby iNaturalist observations, species summaries, and favorite controls.

## Architecture

The project uses three executable entry points:

- `prep_data.py` downloads and processes Michigan DNR trail data.
- `prep_historical_observations.py` documents the one-time conversion of the manually downloaded historical iNaturalist CSV export into an app-ready Parquet file.
- `app.py` runs the Streamlit interface.

Reusable code is organized under `src/`:

```text
src/
├── apis/
│   ├── dnr_api.py
│   └── inaturalist_api.py
├── trails.py
├── locations.py
├── spatial.py
├── inaturalist.py
└── maps.py
```

API modules contain HTTP request and API-response validation logic only. Data cleaning, spatial calculations, summaries, mapping, and Streamlit rendering remain outside the API modules.

Spatial distance calculations use Michigan GeoRef (`EPSG:3078`). Folium map geometry uses WGS 84 (`EPSG:4326`).

## Project Structure

```text
Whats_UP_Outdoors/
├── app.py
├── prep_data.py
├── prep_historical_observations.py
├── README.md
├── SPEC.md
├── requirements.txt
├── AI_USE_DISCLOSURE.md
├── static/
│   ├── banner.png
│   └── map_up.jpg
├── data/
│   ├── raw/
│   └── processed/
│       ├── dnr_up_hiking_trails_grouped.parquet
│       └── inaturalist_historical_fall_observations.parquet
├── src/
│   ├── apis/
│   │   ├── dnr_api.py
│   │   └── inaturalist_api.py
│   ├── trails.py
│   ├── locations.py
│   ├── spatial.py
│   ├── inaturalist.py
│   └── maps.py
└── tests/
```

## Data

### Michigan DNR trails

`prep_data.py` downloads current Upper Peninsula hiking-trail data from the Michigan DNR ArcGIS REST API, validates the response, cleans and groups trail segments, and writes the app-ready GeoParquet dataset.

Trail length uses the DNR-reported segment lengths aggregated for each grouped trail. During development, projected geometry lengths are compared manually in the audit workflow to verify that the reported values are reasonable for the MVP.

### iNaturalist observations

Recent observations are requested from the iNaturalist API at runtime for the previous 21 days.

Historical observations come from a manually downloaded export that is already scoped to the Upper Peninsula area and September–October 2015–2025. The raw CSV remains local. `prep_historical_observations.py` documents the cleaning and conversion process used to create:

```text
data/processed/inaturalist_historical_fall_observations.parquet
```

The processed historical Parquet file is committed for the local demo.

iNaturalist records represent reported observations, not a guarantee that a species will be present.

## Setup

Create and activate a Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Project

Prepare the DNR trail data:

```powershell
python prep_data.py
```

Run the automated tests:

```powershell
pytest
```

Start the Streamlit application:

```powershell
streamlit run app.py
```

## Data Sources

- Michigan DNR Hiking Trails Open Data
- iNaturalist Observations API and manually downloaded historical observations
- GeoNames postal-code data through `pgeocode`

## Technologies

Python, pandas, GeoPandas, Shapely, Streamlit, Folium, streamlit-folium, Requests, PyArrow, pgeocode, and pytest.

## Limitations

- ZIP-code distance is straight-line spatial distance from the ZIP-code reference point to the trail geometry, not driving distance.
- DNR attributes may be missing or vary across grouped trail segments.
- Trail status reflects the DNR source field and may not represent current on-site conditions.
- Historical iNaturalist observations are fixed to September and October 2015–2025.
- Recent observation availability depends on the iNaturalist API.
- The app does not provide navigation, safety guidance, or wildlife guarantees.

See [`SPEC.md`](SPEC.md) for the complete MVP requirements.
