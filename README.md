![What's UP Outdoors banner](assets/banner.png)

# What’s UP Outdoors: Upper Peninsula Trail Explorer

What’s UP Outdoors is a Python and Streamlit portfolio project for discovering hiking trails and nearby iNaturalist observations in Michigan’s Upper Peninsula.

The MVP emphasizes reproducible geospatial processing, API integration, automated testing, and a maintainable modular structure.

> **Status:** MVP specification complete; implementation in progress.

## MVP Features

- Search from a United States ZIP code
- Choose a 10, 25, or 50 mile radius
- View up to five nearby trails, ordered by distance
- Compare trail name, county, status, length, width, surface, and distance
- Explore returned trails on a Folium map
- Select a trail to open its dashboard
- Map observations within two miles of the selected trail
- Distinguish recent observations with orange stars and historical observations with blue X markers
- View the top five species within each supported taxon group
- Continue showing historical results if the recent iNaturalist API request fails

## Architecture

The project uses two executable entry points:

- `prep_data.py` downloads and processes Michigan DNR trail data.
- `app.py` runs the Streamlit interface.

Reusable code is organized under `src/`:

```text
src/
├── dnr.py
├── trails.py
├── maps.py
├── locations.py
├── inaturalist.py
└── geospatial.py
```

Spatial calculations use Michigan GeoRef (`EPSG:3078`). Folium map geometry uses WGS 84 (`EPSG:4326`).

## Project Structure

```text
whats-up-outdoors/
├── app.py
├── prep_data.py
├── spec.md
├── assets/
│   ├──banner.png
│   └── map_up.jpg
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── apis
│   │   ├── dnr_api.py
│   ├── __init__.py
│   ├── trails.py
│   ├── maps.py
│   ├── locations.py
│   ├── inaturalist.py
│   └── geospatial.py
├── tests/
│   ├── test_trails.py
│   ├── test_dnr.py
│   └── test_spatial.py
├── README.md
├── SPEC.md
├── AI_USE_DISCLOSURE.md
└── requirements.txt
```

## Data

### Michigan DNR trails

`prep_data.py` downloads current Upper Peninsula hiking-trail data from the Michigan DNR ArcGIS REST API.

- Raw API responses are saved under `data/raw/`.
- Processed trail data is saved under `data/processed/` as GeoParquet.
- Generated DNR files are excluded from Git.

### iNaturalist observations

- Recent observations from the previous 14 days are requested at runtime.
- Historical September and October observations from 2015 through 2025 are stored as a fixed committed Parquet dataset.

iNaturalist records indicate reported observations, not the likelihood that a species will be present.

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
- iNaturalist Observations API and exported observations
- GeoNames postal-code data through `pgeocode`

## Technologies

Python, pandas, GeoPandas, Shapely, Streamlit, Folium, Requests, PyArrow, pgeocode, and pytest.

## Limitations

- ZIP-code distance uses the ZIP-code reference point, not driving distance.
- DNR attributes may be missing or vary across grouped trail segments.
- Trail status reflects the DNR source field and may not represent current on-site conditions.
- Historical iNaturalist observations are fixed to September and October 2015–2025.
- Recent observation availability depends on the iNaturalist API.
- The app does not provide navigation, safety guidance, or wildlife guarantees.

See [`SPEC.md`](SPEC.md) for the complete MVP requirements.
