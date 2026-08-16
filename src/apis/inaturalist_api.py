"""HTTP requests and response validation for the iNaturalist API."""

from datetime import date, timedelta

import requests

from src.inaturalist import (
    TAXON_GROUPS
)


API_URL = "https://api.inaturalist.org/v1/observations"
MAX_PAGES = 5
PER_PAGE = 200
DAYS_RETRIEVED = 21


HEADERS = {"User-Agent": "Whats-UP-Outdoors/0.2"}

def fetch_recent_observations(bounds, timeout = 60):
    """Fetch iNaturalist observations nearby a selected trail."""
    end_date = date.today()
    start_date = end_date - timedelta(days= DAYS_RETRIEVED - 1)

    west, south, east, north = (
        bounds.to_crs("EPSG:4326").total_bounds
    )
    
    params = {
        "swlat": south,
        "swlng": west,
        "nelat": north,
        "nelng": east,
        "d1": start_date.isoformat(),
        "d2": end_date.isoformat(),
        "verifiable": "true",
        "mappable": "true",
        "iconic_taxa": ",".join(TAXON_GROUPS.values()),
        "per_page": PER_PAGE,
        "order_by": "observed_on",
        "order": "desc"
    }

    results = []

    for page in range(1, MAX_PAGES + 1):
        params["page"] = page

        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=timeout
        )
        response.raise_for_status()

        data = response.json()

        if "results" not in data or "total_results" not in data:
            raise ValueError(
                "Unexpected response from iNaturalist API"
            )

        page_results = data.get("results")
        total_results = data.get("total_results")

        if not isinstance(page_results, list):
            raise ValueError(
                "iNaturalist API results must be a list."
            )

        results.extend(page_results)

        if not page_results or len(results) >= total_results:
            break

    return results

