# What’s UP Outdoors

[![Live App](https://img.shields.io/badge/Live_App-Launch-FF4B4B?logo=streamlit&logoColor=white)](https://whatsupoutdoors-c5jtsxgkfmw9qkuhrnerhq.streamlit.app/)
[![Technical Spec](https://img.shields.io/badge/Technical_Spec-Documentation-0969DA?logo=readthedocs&logoColor=white)](SPEC.md)
[![AI Use Disclosure](https://img.shields.io/badge/AI_Use-Disclosure-6F42C1?logo=openai&logoColor=white)](AI_USE_DISCLOSURE.md)
[![Project Reflection](https://img.shields.io/badge/Project_Reflection-Blog-F57C00?logo=blogger&logoColor=white)](https://arayofdata.blogspot.com/2026/08/whats-UP-data.html)


**What’s UP Outdoors** is a Python and Streamlit application for exploring hiking trails and nearby iNaturalist observations across Michigan’s Upper Peninsula.

## Overview

The app combines Michigan DNR trail data with recent and historical iNaturalist observations to help users discover trails, compare trail characteristics, and explore reported plants and wildlife nearby.

I started the project while planning a fall-color trip through Michigan’s Upper Peninsula and wanted a practical way to compare hiking options and nearby nature observations.

Users can search by ZIP code, filter trails, explore interactive maps, inspect trail details and observations, generate AI trail summaries, and save favorite trails with notes during the current Streamlit session.

The project also demonstrates geospatial analysis, API integration, reproducible data preparation, Streamlit development, and automated testing.

## Using the App

The application has five main tabs.

### Browse & Filter Trails

Search from a U.S. ZIP code or filter by trail length, surface, and name. ZIP searches return up to 20 nearby trails ordered from nearest to farthest.

<p align="center">
  <img src="static/screenshot_tab1.png" alt="Browse & Filter Trails" width="900">
</p>

### Explore Trails on Map

View the current trail results on an interactive Folium map and inspect trail information directly from the map.

<p align="center">
  <img src="static/screenshot_tab2.png" alt="Explore Trails Map" width="900">
</p>

### Selected Trail Details

Select a trail to view its characteristics, full geometry, recent iNaturalist observations from the last 21 days, historical September–October observations from 2015–2025, species summaries, and favorite controls.

Observations are filtered to those reported within two miles of the selected trail.

<p align="center">
  <img src="static/screenshot_tab3.png" alt="Selected Trail Details" width="900">
</p>

### AI Trail Summary

Generate an on-demand Google Gemini overview using selected trail details, recent nearby observations, and historical observation-density data.

<p align="center">
  <img src="static/screenshot_tab4.png" alt="AI Trail Summary" width="900">
</p>

### Saved Favorite Trails

Compare saved trails in a table and map, reopen trail details, add notes, remove favorites, and download saved trail data. Notes and generated AI summaries are stored for the current Streamlit session.

<p align="center">
  <img src="static/screenshot_tab5.png" alt="Saved Favorite Trails" width="900">
</p>

## Launch the App

[Open What’s UP Outdoors](https://whatsupoutdoors-c5jtsxgkfmw9qkuhrnerhq.streamlit.app/)

Local development, testing, and ETL reproduction instructions are documented in [`SPEC.md`](SPEC.md).

## Limitations

- ZIP-to-trail distance is straight-line spatial distance, not driving distance.
- Trail status reflects the Michigan DNR source and may not represent current on-site conditions.
- Historical iNaturalist data is limited to September–October 2015–2025, and recent observation availability depends on the iNaturalist API.
- iNaturalist observations are reported sightings and do not guarantee species presence.
- AI summaries use supplied project data and do not retrieve current trail news, conditions, or parking information. Adding live web search for those features would require an external or paid web-search-capable API.
- The app is intended for exploration and trip planning, not navigation or safety guidance.

## Future Enhancements

- **Short-term weather forecasts:** Add forecast data for the selected trail area to the AI overview to support trip planning.
- **AI-assisted parking and current trail information:** Retrieve nearby parking and recent trail news or conditions using web search or another external data source.
- **Automated data refresh pipeline:** Periodically refresh and validate source datasets through an automated ETL workflow.

## Tools and Technologies

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data_Processing-150458?logo=pandas&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Geospatial-139C5A)
![Shapely](https://img.shields.io/badge/Shapely-Spatial_Analysis-3776AB)
![Folium](https://img.shields.io/badge/Folium-Interactive_Maps-77B829)
![iNaturalist](https://img.shields.io/badge/iNaturalist-REST_API-74AC00)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI_Summaries-4285F4?logo=googlegemini&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP-333333)
![PyArrow](https://img.shields.io/badge/PyArrow-Parquet-005571)
![pgeocode](https://img.shields.io/badge/pgeocode-ZIP_Geocoding-555555)
![pytest](https://img.shields.io/badge/pytest-Testing-0A9EDC?logo=pytest&logoColor=white)


## Project Structure

```text
Whats_UP_Outdoors/
├── app.py                                  # Streamlit application entry point
├── README.md                               # Project overview and usage
├── SPEC.md                                 # Technical MVP specification
├── requirements.txt                        # Python dependencies
├── AI_USE_DISCLOSURE.md                    # AI-assisted work disclosure
├── static/                                 # App images
├── util/                                   # Offline ETL workflows
│   ├── etl_dnr_trails.py                   # Michigan DNR trail ETL
│   └── etl_inaturalist_history.py          # Historical iNaturalist ETL
├── notebooks/                              # Exploratory analysis
├── reports/                                # Generated profiling output
├── data/
│   ├── raw/                                # Local ETL source data
│   └── processed/                          # App-ready Parquet datasets
├── src/                                    # Reusable application logic
│   ├── apis/                               # External API helpers
│   │   ├── dnr_api.py
│   │   ├── genai_api.py
│   │   └── inaturalist_api.py
│   ├── ai.py                               # AI summary preparation/generation
│   ├── trails.py                           # Trail processing and filtering
│   ├── locations.py                        # ZIP validation and geocoding
│   ├── spatial.py                          # Spatial calculations and filtering
│   ├── inaturalist.py                      # Observation processing/summaries
│   ├── streamlit_ui.py                     # Streamlit UI helpers and favorites
│   └── maps.py                             # Folium maps
└── tests/                                  # Pytest suite
```
