# What’s UP Outdoors: Upper Peninsula Trail Explorer

**Status:** MVP baseline  
**Version:** 0.5  
**Application:** Local Streamlit application with a standalone data-preparation pipeline

## 1. Purpose

**What’s UP Outdoors** helps users discover hiking trails in Michigan’s Upper Peninsula and review nearby iNaturalist observations.

- **Primary goal:** Demonstrate a documented, reproducible, tested, and maintainable geospatial data workflow using Python, pandas, GeoPandas, and Parquet.
- **Secondary goal:** Provide a clean trail-discovery interface with an interactive map and trail-results table.

## 2. Architecture and Technology

The project uses two executable entry points supported by focused Python modules.

### Entry points

#### `prep_data.py`: Offline data preparation

`prep_data.py` must:

- Download raw Michigan DNR trail data from the DNR API.
- Save the unmodified response under `data/raw/`.
- Run trail validation, cleaning, grouping, and spatial processing.
- Save the processed trail dataset under `data/processed/` as GeoParquet.

It must not download recent or historical iNaturalist data.

#### `app.py`: Streamlit interface

`app.py` must:

- Define the interactive user flow.
- Load processed trail data.
- Load the committed historical iNaturalist dataset.
- Handle ZIP-code location searches.
- Fetch recent iNaturalist observations after a trail is selected.
- Render Folium maps and data summaries.

Raw-data cleaning and spatial calculations must be implemented outside `app.py`.

### Core modules

Place the project modules under `src/whats_up_outdoors/`:

- `trails.py`: DNR download, validation, cleaning, grouping, and trail summaries
- `locations.py`: ZIP-code normalization, validation, and `pgeocode` coordinate lookup
- `inaturalist.py`: Recent API requests, historical-data loading, taxon mapping, and species summaries
- `spatial.py`: Coordinate reference system transformations, length calculations, point-to-geometry distance, and spatial filtering

Add another module only when an existing module becomes difficult to understand or develops unrelated responsibilities.

### Technology stack

- **Core:** `streamlit`, `pandas`, `geopandas`, `folium`, `streamlit-folium`, `requests`, `pgeocode`, `pyarrow`
- **Testing:** `pytest`

Use `python-dotenv` only if environment variables or credentials are required.

Do not add dependencies unless they provide a clear benefit that cannot reasonably be handled by the existing stack.

## 3. Project Data Policy

### Committed data

The repository must include the fixed historical iNaturalist dataset for September and October 2015 through 2025.

This dataset is downloaded manually before development and is never refreshed by `prep_data.py`.

### Locally generated data

The following data must be excluded from Git:

- `data/raw/`: Raw Michigan DNR API responses
- `data/processed/`: Processed DNR trail GeoParquet files
- Runtime API-response caches

## 4. Data Sources

### Michigan DNR trails

- **Layer endpoint:** `https://gisagodnr.state.mi.us/arcgis/rest/services/DNR/DNRTrailsOPENDATA/MapServer/2`
- **Required fields:** Geometry, trail name, county, width, surface type, trail status, and relevant source identifiers
- **Scope:** Hiking trails in Michigan’s Upper Peninsula
- **Status rule:** Preserve the DNR-provided status value. Display `Unknown` when no status is available. Do not derive custom status values.

### iNaturalist observations

- **Recent:** Observations from the previous 14 days, fetched from the iNaturalist REST API at runtime after a trail is selected
- **Historical:** Fixed September and October observations from 2015 through 2025

### ZIP-code geocoding

Use `pgeocode` to convert United States ZIP codes into latitude and longitude.

## 5. Coordinate Reference Systems

### Spatial processing

Use **Michigan GeoRef (`EPSG:3078`)** for:

- Trail-length calculations
- User-to-trail distance calculations
- Observation-to-trail distance calculations
- Radius filtering

Convert displayed lengths and distances from meters to miles.

### Mapping

Use **WGS 84 (`EPSG:4326`)** for all Folium map geometries.

Reproject geometries to `EPSG:4326` only after spatial calculations are complete.

### CRS rules

- Confirm the source CRS before reprojection.
- Do not assign a CRS without supporting source metadata or documentation.
- Do not use trail centroids as substitutes for point-to-geometry nearest-distance calculations.

## 6. Data-Preparation Requirements

`prep_data.py` must:

1. Fetch DNR trail data from the API.
2. Save the raw response under `data/raw/`.
3. Validate required columns.
4. Confirm that geometries are present and valid.
5. Confirm the source CRS before reprojection.
6. Filter the data to Upper Peninsula hiking trails.
7. Group raw segments by normalized trail name and county.
8. Calculate grouped trail length in miles using `EPSG:3078`.
9. Aggregate width, surface, and status values.
10. Export a lean GeoParquet dataset under `data/processed/`.

The same normalized trail name in different counties must produce separate grouped trails.

Repeated trail names must not automatically be treated as duplicate source records.

Each grouped trail must retain:

- Trail name
- County
- Merged geometry
- Total calculated length in miles
- Width summary
- Surface summary
- Status summary
- Relevant source identifiers

### Width aggregation

- Use one value when all valid segment values agree.
- Use `Varies` when valid values differ.
- Use `Unknown` when no valid value is available.

### Surface aggregation

- Use one value when all valid segment values agree.
- Use a comma-separated list of distinct values when multiple surfaces are present.
- Use `Unknown` when no valid value is available.

### Status aggregation

- Preserve the DNR-provided value.
- Use one value when all valid segment values agree.
- Use a comma-separated list of distinct values when statuses differ.
- Use `Unknown` when no valid value is available.

## 7. Location Search and Spatial Filtering

The user must enter a United States ZIP code and select one search radius:

- 10 miles
- 25 miles
- 50 miles

The application must:

1. Normalize and validate the ZIP-code input.
2. Resolve latitude and longitude using `pgeocode`.
3. Create a point geometry in `EPSG:4326`.
4. Reproject the point to `EPSG:3078`.
5. Calculate the shortest distance from the point to each trail geometry.
6. Retain trails within the selected radius.
7. Sort matching trails from nearest to farthest.
8. Return no more than five trails.

Display a clear user-facing message when:

- The ZIP code is missing or invalid.
- `pgeocode` cannot resolve the ZIP code.
- No Upper Peninsula trails are found within the selected radius.

Expected input errors must not expose raw stack traces.

## 8. Selected-Trail Dashboard and iNaturalist Integration

When the user selects a trail, render the dashboard in the following order:

1. Selected-trail heading and attributes
2. Selected-trail observation map
3. Recent taxon summaries
4. Historical taxon summaries

### Selected-trail attributes

Display:

- Trail name
- County
- Status
- Total length in miles
- Surface
- Width
- Distance from the entered ZIP code in miles

### Selected-trail observation map

Display a Folium map that:

- Shows the complete selected-trail geometry in `EPSG:4326`.
- Is centered and zoomed to the selected trail and qualifying observations.
- Shows observations within two miles of the trail geometry.
- Uses orange star markers for recent observations.
- Uses blue X markers for historical observations.
- Includes a legend identifying both marker types.

Observation-to-trail distance must be calculated in `EPSG:3078` using true point-to-geometry distance.

Only qualifying observations may appear on the map or in the summaries.

If the recent API request fails:

- Display a clear error message.
- Continue rendering the trail and historical observations.
- Do not crash the dashboard.

If either observation period has no qualifying results, continue displaying the trail and any available observations from the other period.

Exclude observations with missing or invalid coordinates without crashing the application.

### Taxon groups

Use the following mapping as the single source of truth:

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

Observations outside these groups must not appear in the species summaries.

### Species summaries

For both recent and historical observations:

- Group observations by taxon group.
- Rank species by observation count.
- Display no more than five species per taxon group.
- Use the most recent observation date as the secondary sort key when counts are equal.

Each displayed species must include:

- Common or display name
- Observation count
- Most recent observation date
- Thumbnail image, when available

Missing observations, names, taxon values, dates, or thumbnails must not cause the application to fail.

Recent and historical summaries must remain visually distinct.

## 9. Testing Requirements

Use `pytest` with small, deterministic fixtures.

Automated tests must not depend on live external APIs.

### Unit tests

Cover:

- Trail-name normalization
- Required-column validation
- Width aggregation
- Surface aggregation
- Status aggregation
- ZIP-code normalization and validation
- Taxon mapping
- Species ranking
- Date tie-breaking
- Missing-value behavior

### Geospatial tests

Cover:

- `EPSG:4326` to `EPSG:3078` conversion
- `EPSG:3078` to `EPSG:4326` conversion
- Trail-length calculations
- True point-to-geometry nearest distance
- Confirmation that centroids are not used for proximity
- Radius filtering
- Two-mile observation filtering
- Nearest-first sorting
- Five-trail result limits
- Exclusion of observations with missing or invalid coordinates

### API tests

Use mocked DNR and iNaturalist responses to cover:

- Successful responses
- Empty responses
- Invalid or incomplete data
- HTTP 4xx and 5xx responses
- Timeouts
- Connection failures
- Historical-data fallback when the recent iNaturalist request fails
- Preservation of the raw DNR response before processing

### Integration tests

Cover:

- Raw DNR fixture to processed GeoParquet output
- Processed trail data loading
- ZIP-code point to filtered and sorted trail results
- Selected trail to filtered historical observation summary
- Selected trail to map-ready trail and observation geometries
- Correct orange star and blue X marker assignments
- Dashboard behavior when either recent or historical observations are unavailable

Organize tests by module:

```text
tests/
├── conftest.py
├── test_trails.py
├── test_locations.py
├── test_inaturalist.py
├── test_spatial.py
└── test_pipeline.py
```

The complete test suite must run with:

```bash
pytest
```

## 10. Non-Goals

The MVP does not include:

- Browser-based GPS geolocation
- Automated historical iNaturalist updates
- Weather integration
- Driving-distance calculations
- Route navigation
- Turn-by-turn directions
- User authentication
- Saved favorites, reviews, or ratings
- Production database storage
- Machine-learning recommendations
- Automated trail difficulty or safety ratings
- Real-time wildlife guarantees
- Hosted production infrastructure
- A mobile application
