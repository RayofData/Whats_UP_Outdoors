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

## Future Enhancements

* **AI-generated natural-language summaries:** Use an AI API to summarize selected trail attributes and nearby observation data in clear, grounded language.
* **Automated data refresh pipeline:** Automate DNR data refreshes and validation through a scheduled ETL workflow, such as GitHub Actions.
* **Downloadable trail reports:** Generate a report for a selected trail containing trail details, maps, observation summaries, and other key information.


## Application Layout

The Streamlit app uses four main tabs:

1. **Trails** — displays all trails before a ZIP search and up to 20 nearby trails after a search.
2. **Map** — displays the corresponding trail set on an interactive Folium map.
3. **Trail Details** — allows selection of any Upper Peninsula trail and displays trail attributes, nearby iNaturalist observations, species summaries, and favorite controls.
4. **Favorite Trails** — displays favorite trails, include a map, and option to save as csv.

## Architecture

The project separates application runtime, offline ETL workflows, and reusable application logic.

### Application
app.py is the Streamlit application entry point.
The deployed application reads the processed trail and historical iNaturalist Parquet datasets directly from data/processed/.
Runtime API requests, spatial operations, mapping, and interface logic are delegated to modules under src/.

### Offline ETL utilities

Data-preparation workflows are stored under util/:

util/etl_dnr_trails.py downloads Michigan DNR trail data, validates and transforms the source data, and creates the app-ready trail GeoParquet dataset.
util/etl_inaturalist_history.py converts the manually downloaded historical iNaturalist CSV export into the compressed Parquet dataset used by the application.

These ETL scripts are used to reproduce or refresh the processed datasets and are not required during normal application startup.

### Reusable modules

```text
src/
├── apis/
│   ├── dnr_api.py
│   └── inaturalist_api.py
├── trails.py
├── locations.py
├── spatial.py
├── inaturalist.py
├── streamlit_ui.py
└── maps.py
```

API modules contain HTTP request and API-response validation logic only. Data cleaning, spatial calculations, summaries, mapping, and Streamlit rendering remain outside the API modules.

Spatial distance calculations use Michigan GeoRef (`EPSG:3078`). Folium map geometry uses WGS 84 (`EPSG:4326`).

## Project Structure

```text
Whats_UP_Outdoors/
├── app.py
├── README.md
├── SPEC.md
├── requirements.txt
├── AI_USE_DISCLOSURE.md
├── static/
│   ├── banner.png
│   └── map_up.jpg
├── util/
│   ├── etl_dnr_trails.py
│   └── etl_inaturalist_history.py
├── data/
│   ├── raw/
│   └── processed/
│       ├── dnr_up_hiking_trails_grouped.parquet
│       └── inaturalist_historical_up_fall_observations.parquet
├── src/
│   ├── apis/
│   │   ├── dnr_api.py
│   │   └── inaturalist_api.py
│   ├── trails.py
│   ├── locations.py
│   ├── spatial.py
│   ├── inaturalist.py
│   ├── streamlit_up.py
│   └── maps.py
└── tests/
```

## Run the Application
### Browser

What’s UP Outdoors is intended to be deployed with Streamlit Community Cloud.

Once deployed, the application can be opened directly in a web browser without cloning the repository, installing Python, or preparing the source datasets locally.

Live application: *Streamlit deployment link will be added here.*

The processed DNR trail and historical iNaturalist datasets required by the application are bundled with the repository for the deployed demo.

### Local development

Local setup is only required for development or reproducing the data-processing workflows.

Create and activate a Python 3.12 virtual environment:

```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:
```
python -m pip install -r requirements.txt
```
Run the automated tests:
```
pytest
```
Start the application locally:
```
streamlit run app.py
```

### Rebuild the processed datasets

The processed datasets are already available to the application. These commands are only needed when reproducing or refreshing the source-data pipelines.

Rebuild the Michigan DNR trail dataset:
```
python util/etl_dnr_trails.py
```
Rebuild the historical iNaturalist dataset:
```
python util/etl_inaturalist_history.py
```
The historical iNaturalist workflow requires the [manually downloaded source CSV](https://www.inaturalist.org/observations/export?quality_grade=any&identifications=any&swlat=45.0764339&swlng=-90.4181358&nelat=48.3060628&nelng=-83.4335579&month%5B%5D=9&month%5B%5D=10&verifiable=true&d1=2015-01-01&spam=false) to be present under data/raw/.

## Data and Sources

What’s UP Outdoors uses three external data sources:

* **Michigan DNR Hiking Trails Open Data** for Upper Peninsula trail geometry and attributes.
* **iNaturalist** for recent and historical nature observations.
* **GeoNames postal-code data through `pgeocode`** for ZIP-code lookup.

The processed DNR trail dataset is produced by `util/etl_dnr_trails.py` from the Michigan DNR ArcGIS REST API. Trail segments are cleaned, grouped, and stored as an app-ready GeoParquet dataset.

Recent iNaturalist observations are requested from the API at runtime for the previous 21 days. Historical observations come from a manually downloaded September–October 2015–2025 export and are converted to Parquet by `util/etl_inaturalist_history.py`.

Processed datasets required by the deployed application are included in the repository. Raw source data remains local.

## Technologies

Python, pandas, GeoPandas, Shapely, Streamlit, Folium, streamlit-folium, Requests, PyArrow, pgeocode, and pytest.

## Limitations

* ZIP-to-trail distance is straight-line spatial distance to the trail geometry, not driving distance.
* DNR attributes may be missing or vary across grouped trail segments.
* Trail status reflects the DNR source data and may not represent current on-site conditions.
* Historical iNaturalist observations are limited to September–October 2015–2025.
* Recent observation availability depends on the iNaturalist API.
* iNaturalist observations represent reported sightings and do not guarantee species presence.
* The application does not provide navigation, safety guidance, or wildlife guarantees.

See [`SPEC.md`](SPEC.md) for the complete MVP requirements.
