# What’s UP Outdoors: Upper Peninsula Trail Explorer

**Status:** MVP in development  
**Version:** 0.7  
**Application:** Local Streamlit application with standalone DNR and historical-observation preparation workflows

## 1. Purpose

**What’s UP Outdoors** helps users discover hiking trails in Michigan’s Upper Peninsula and review nearby iNaturalist observations.

- **Primary goal:** Demonstrate a reproducible, tested, and maintainable geospatial data workflow using Python, pandas, GeoPandas, Shapely, APIs, and Parquet.
- **Secondary goal:** Provide a clean local Streamlit interface for ZIP-based trail discovery, mapping, trail details, wildlife observations, and session-based favorites.

## 2. Architecture

### Entry points

1. **`prep_data.py`**  
   Downloads Michigan DNR trail data, saves the raw response under `data/raw/`, validates and processes the trails, and writes the app-ready DNR GeoParquet locally.

2. **`prep_historical_observations.py`**  
   One-time reproducibility script for converting the manually downloaded historical iNaturalist CSV into:

   `data/processed/inaturalist_historical_fall_observations.parquet`

   The raw CSV remains local and Git-ignored. The processed historical Parquet is committed to the repository.

3. **`app.py`**  
   Defines Streamlit UI flow and coordinates module calls. It does not directly perform raw-data cleaning, HTTP requests, spatial calculations, or Folium map construction.

### Core modules

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

Responsibilities:

- `apis/dnr_api.py`: DNR HTTP requests, batching, service-response validation, raw-download validation, and profiling.
- `apis/inaturalist_api.py`: iNaturalist HTTP requests, pagination, parameters, and API-response validation.
- `trails.py`: trail cleaning, normalization, grouping, aggregation, and length categories.
- `locations.py`: ZIP normalization, validation, `pgeocode` lookup, and user point creation.
- `spatial.py`: CRS transformations, distance calculations, radius filtering, nearest-trail filtering, and related spatial operations.
- `inaturalist.py`: historical Parquet loading, recent-observation normalization, taxon mapping, and species summaries.
- `maps.py`: Folium map construction.

`*_api.py` modules contain HTTP/service-response logic only. They must not perform application data cleaning, spatial calculations, map construction, or Streamlit rendering.

### Technology

- Core: `streamlit`, `pandas`, `geopandas`, `shapely`, `folium`, `streamlit-folium`, `requests`, `pgeocode`, `pyarrow`
- Testing: `pytest`
- Do not add dependencies without explicit approval.

## 3. Data Policy and Sources

### Michigan DNR trails

Source:

`https://gisagodnr.state.mi.us/arcgis/rest/services/DNR/DNRTrailsOPENDATA/MapServer/2`

- Scope: Upper Peninsula hiking trails.
- Raw API responses are local and Git-ignored.
- Processed DNR GeoParquet is generated locally and is not committed.
- Preserve DNR-provided trail status values. Use `Unknown` when no usable status is available.

### Historical iNaturalist observations

- Manually downloaded fixed export.
- Geographic scope is already centered on the Upper Peninsula area.
- May include nearby Wisconsin and Canadian observations.
- September–October, 2015–2025.
- Raw CSV remains local and Git-ignored.
- Processed Parquet is committed.

### Recent iNaturalist observations

- Fetched at runtime from the iNaturalist REST API.
- Uses the previous 21 days.

### ZIP geocoding

Use `pgeocode` to resolve valid United States ZIP codes into latitude and longitude.

## 4. Spatial Rules

Use:

- **WGS 84 (`EPSG:4326`)** for ZIP coordinates, iNaturalist coordinates, and Folium map rendering.
- **Michigan GeoRef (`EPSG:3078`)** for distance calculations.

Before distance calculations:

1. Confirm or define the known source CRS.
2. Reproject with `.to_crs("EPSG:3078")`.
3. Use the actual trail geometry, not a centroid.
4. Convert calculated meters to miles.

### Required distance behavior

- ZIP-to-trail distance: shortest distance from ZIP point to actual trail line or multiline geometry.
- Observation-to-trail distance: shortest distance from observation point to actual selected-trail geometry.
- A qualifying observation has a shortest point-to-trail distance of **≤ 2 miles in `EPSG:3078`**.

The exact iNaturalist API query-area construction is an implementation detail. The final local two-mile spatial filter is authoritative.

## 5. DNR Trail Preparation

`prep_data.py` must:

1. Download matching DNR trail features.
2. Save the raw response locally.
3. Validate the download.
4. Replace known placeholder values defined in `PLACEHOLDER_VALUES`.
5. Apply the existing trail-name normalization.
6. Group trail segments by normalized trail name and county.
7. Aggregate trail attributes.
8. Add trail length categories.
9. Save the local app-ready DNR GeoParquet.

Repeated trail names in different counties remain separate trails.

### Aggregation rules

- **Length:** sum DNR `SegmentLengthMiles` into `ReportedLengthMiles`.
- **Length category:**  
  - Short: ≤ 2 miles  
  - Medium: > 2 and ≤ 7 miles  
  - Long: > 7 miles
- **Width:** one value if all valid segments agree, `Varies` if they differ, `Unknown` if none are valid.
- **Surface:** one value if all valid segments agree; otherwise comma-separated unique values; `Unknown` if none are valid.
- **Status:** preserve DNR values; use one value if all valid segments agree; otherwise comma-separated unique values; `Unknown` if none are valid.

Geometry-derived trail lengths were manually audited against DNR-reported values. Production uses `ReportedLengthMiles`.

## 6. Historical Observation Preparation

`prep_historical_observations.py` is a one-time reproducibility script and is not part of normal app startup or `prep_data.py`.

The source export is already geographically scoped and already limited to September–October 2015–2025.

The script must:

- validate that dates remain within September–October 2015–2025
- keep quality grades `research` and `needs_id`
- keep only supported taxon groups
- require a species-level scientific name
- require valid latitude and longitude
- exclude obscured coordinates
- remove duplicate observation IDs
- retain positional accuracy without enforcing a hard cutoff
- preserve nearby Wisconsin and Canadian observations
- avoid applying an additional Michigan-only or UP-boundary filter

Normalize to:

```text
observation_id
observed_on
common_name
scientific_name
iconic_taxon
thumbnail_url
longitude
latitude
positional_accuracy
```

## 7. ZIP Search and Nearby Trails

The user may enter any valid U.S. ZIP code and choose:

- 10 miles
- 25 miles
- 50 miles

Search flow:

1. Validate and normalize the ZIP.
2. Resolve lat/lon with `pgeocode`.
3. Create the ZIP point in `EPSG:4326`.
4. Reproject the ZIP point and trails to `EPSG:3078`.
5. Calculate true point-to-trail distance.
6. Keep trails inside the selected radius.
7. Sort nearest to farthest.
8. Return at most 20 trails.

### Search outcomes

- **Valid ZIP + matches:** show up to 20 nearest trails.
- **Valid ZIP + no matches:** show an empty table and a normal informational message such as `No trails found within 25 miles.`
- **Invalid or unresolved ZIP:** show validation feedback and do not run the distance search.
- Expected user input errors must not expose raw stack traces.

## 8. Streamlit UI

Use `st.session_state` for favorites and other state that must persist across Streamlit reruns.

### Sidebar

- Display session favorites.
- Provide CSV export for favorites.
- Export fields exactly:
  - Trail
  - County
  - Length
  - Surface
  - Width

### Tab 1: Trails

Before ZIP search:

- display all grouped UP trails

After ZIP search:

- display up to 20 matching trails
- sort nearest first
- include `Distance from ZIP`
- show the number of matching trails
- total UP trail count may also be displayed if it fits naturally

Displayed fields:

- Trail
- County
- Length Category
- Length (Miles)
- Width
- Surface
- Status
- Distance from ZIP when applicable

### Trail selection

Tab 1 is the single source of truth for selected trail state.

- The user selects a trail in Tab 1.
- Store the selected trail in `st.session_state`.
- ZIP search is not required before selecting a trail.
- Tab 3 must not contain a separate competing trail selector.

### Tab 2: Map

Before ZIP search:

- display all grouped UP trails

After ZIP search:

- display the same maximum-20 result set shown in Tab 1
- include the ZIP reference point when useful

### Tab 3: Trail Details

If no trail has been selected in Tab 1, show a simple prompt to select one.

For the selected trail, display:

- trail name
- county
- status
- `ReportedLengthMiles`
- length category
- surface
- width
- ZIP distance if available for the current search
- selected-trail observation map
- recent species summaries
- historical species summaries
- add/remove favorite control

## 9. iNaturalist Integration

Use this mapping in `inaturalist.py` as the single source of truth:

```python
TAXON_GROUPS = {
    "Birds": "Aves",
    "Mammals": "Mammalia",
    "Plants": "Plantae",
    "Fungi": "Fungi",
    "Reptiles": "Reptilia",
    "Insects": "Insecta",
}
```

Observations outside these groups do not appear in species summaries.

### Recent observations

- Fetch the previous 21 days from the iNaturalist API.
- Normalize API results into the common application schema.
- Apply the required two-mile point-to-trail filter locally.

If the API request fails:

- show `Recent observations unavailable`
- continue displaying the selected trail and historical observations
- do not crash

If the API succeeds but no recent observations qualify:

- show `No recent observations found`
- treat this as a normal result, not an error

### Historical observations

- Load the committed historical Parquet.
- Apply the same authoritative two-mile point-to-trail filter used for recent observations.

### Observation map

The selected-trail map must:

- show the complete trail geometry
- show only qualifying observations
- visually distinguish recent and historical observations
- remain usable when either period has no observations

### Species summaries

Calculate recent and historical summaries separately.

For each period:

- group by supported taxon group
- rank species by observation count
- break count ties using most recent observation date
- show up to 10 species per taxon group
- include display/common name, count, most recent date, and thumbnail when available

Missing optional names or thumbnails must not crash the app.

## 10. Favorites

Favorites are required for the MVP.

- Add/remove favorite from Tab 3.
- Store favorites in `st.session_state`.
- Display favorites in the sidebar.
- Allow CSV download from the sidebar.
- Favorites last for the current Streamlit session.

CSV fields:

```text
Trail
County
Length
Surface
Width
```

## 11. Testing

Use a concise `pytest` suite targeting approximately **8 tests total**. Exact distribution is flexible.

Use small deterministic fixtures. Do not rely on live external APIs.

High-value behaviors include:

- placeholder cleanup
- trail grouping and aggregation
- representative API validation/mocking
- ZIP-to-trail point distance in `EPSG:3078`
- search-radius filtering
- nearest-first ordering
- maximum-20 result behavior
- two-mile observation filtering

Avoid large matrices of low-value HTTP or UI tests for the MVP.

## 12. Guardrails

Do not add these to the MVP:

- browser/device geolocation
- driving-distance or routing features
- weather integration
- machine-learning recommendations
- hosted/production infrastructure

Keep the implementation local, understandable, reproducible, and small enough to explain clearly in an interview.
