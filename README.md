# What’s UP Outdoors

**What’s UP Outdoors** is a Python and Streamlit application for exploring hiking trails and nearby iNaturalist observations across Michigan’s Upper Peninsula.

[Launch the live app](https://whatsupoutdoors-c5jtsxgkfmw9qkuhrnerhq.streamlit.app/) | [Project specification](SPEC.md) | [AI use disclosure](AI_USE_DISCLOSURE.md)

## Overview

The application combines Michigan DNR trail data with recent and historical iNaturalist observations to help users discover trails, compare trail characteristics, and explore nature observations reported nearby.

I started the project while planning a fall-color trip to Michigan’s Upper Peninsula. I wanted a practical way to compare hiking options near the places we might visit and see what plants and wildlife had been observed around those trails during recent and previous fall seasons.

Users can search from a ZIP code, filter trails, explore results on interactive maps, inspect individual trails, and save favorites during the current Streamlit session.

The project also serves as a portfolio demonstration of geospatial analysis, API integration, reproducible data preparation, Streamlit application development, and automated testing.


## Using the App

The application has four main tabs.

### Browse & Filter Trails

Browse all available Upper Peninsula trails or narrow the results using a ZIP code, search radius, trail length, surface type, or trail name.

ZIP searches return up to 20 nearby trails ordered from nearest to farthest.

### Explore Trails on Map

View the current trail results on an interactive map and inspect trail information directly from the map.

### Selected Trail Details

Select a trail from the results table to view:

* trail characteristics
* full trail geometry
* recent iNaturalist observations
* historical fall observations
* species summaries by taxon group

Nearby observations are filtered to those reported within two miles of the selected trail.

### Saved Favorite Trails

Save trails during the current Streamlit session, compare them together, and export the list as a CSV file.

## Run Locally

The easiest way to use the project is through the deployed Streamlit app:

[Open What’s UP Outdoors](https://whatsupoutdoors-c5jtsxgkfmw9qkuhrnerhq.streamlit.app/)

For local development, create and activate a Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the tests:

```powershell
pytest
```

Start the application:

```powershell
streamlit run app.py
```

Processed datasets required by the application are included in the repository, so rebuilding them is not required to run the app.

To reproduce or refresh the processed datasets:

```powershell
python util/etl_dnr_trails.py
python util/etl_inaturalist_history.py
```
The historical iNaturalist workflow requires the [manually downloaded](https://www.inaturalist.org/observations/export?quality_grade=any&identifications=any&swlat=45.0764339&swlng=-90.4181358&nelat=48.3060628&nelng=-83.4335579&month%5B%5D=9&month%5B%5D=10&verifiable=true&d1=2015-01-01&spam=false) source CSV to be present under data/raw/.

See [`SPEC.md`](SPEC.md) for detailed architecture, data-processing, spatial, and testing requirements.

## Limitations

* ZIP-to-trail distance is straight-line spatial distance, not driving distance.
* Trail status reflects the DNR source data and may not represent current on-site conditions.
* Historical iNaturalist observations are limited to September–October 2015–2025.
* Recent observation availability depends on the iNaturalist API.
* iNaturalist observations represent reported sightings and do not guarantee species presence.
* The application is intended for exploration and trip planning, not navigation or safety guidance.

## Future Enhancements

* **AI-generated trail summaries:** Summarize trail characteristics and nearby observation data in grounded natural language.
* **Automated data refresh pipeline:** Periodically refresh and validate source datasets through an automated ETL workflow.
* **Downloadable trail reports:** Generate reports containing trail details, maps, and observation summaries.

## Project Structure

```
Whats_UP_Outdoors/
├── app.py                                  # Streamlit application entry point
├── README.md                               # Project overview and usage instructions
├── SPEC.md                                 # Detailed MVP requirements and architecture
├── requirements.txt                        # Python dependencies
├── AI_USE_DISCLOSURE.md                    # Disclosure of AI-assisted project work
│
├── static/                                 # Images used by the Streamlit interface
│   ├── banner.png                          # Application banner
│   └── map_up.jpg                          # Upper Peninsula sidebar map
│
├── util/                                   # Offline data preparation workflows
│   ├── etl_dnr_trails.py                   # Downloads and processes Michigan DNR trail data
│   └── etl_inaturalist_history.py          # Processes historical iNaturalist observations
│
├── data/
│   ├── raw/                                # Local source data used by ETL workflows
│   └── processed/                          # App-ready datasets
│       ├── dnr_up_hiking_trails_grouped.parquet
│       │                                   # Processed and grouped DNR trail data
│       └── inaturalist_historical_up_fall_observations.parquet
│                                           # Processed historical fall observations
│
├── src/                                    # Reusable application logic
│   ├── apis/                               # External API request logic
│   │   ├── dnr_api.py                      # Michigan DNR API helpers
│   │   └── inaturalist_api.py              # iNaturalist API helpers
│   ├── trails.py                           # Trail cleaning, grouping, and filtering
│   ├── locations.py                        # ZIP validation and geocoding
│   ├── spatial.py                          # Distance and spatial filtering operations
│   ├── inaturalist.py                      # Observation normalization and summaries
│   ├── streamlit_ui.py                     # Reusable Streamlit display helpers
│   └── maps.py                             # Folium map construction
│
└── tests/                                  # Automated pytest test suite
```