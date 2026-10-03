import pandas as pd
import pytest

from src.inaturalist import normalize_recent_observations, summarize_species
from util import etl_inaturalist_history as etl


def export_row(observation_id=1, **overrides):
    return {
        "id": observation_id,
        "observed_on": "2020-09-15",
        "common_name": "red fox",
        "scientific_name": "Vulpes vulpes",
        "iconic_taxon_name": "Mammalia",
        "image_url": "https://example.com/photo.jpg",
        "latitude": 45.0,
        "longitude": -85.0,
        **overrides,
    }


def test_combined_exports_round_trip(tmp_path, monkeypatch):
    up = tmp_path / "up.csv"
    lp = tmp_path / "lp.csv"
    output = tmp_path / "processed" / "combined.parquet"
    pd.DataFrame([
        export_row(scientific_name="Vulpes vulpes fulva", taxon_species_name="Vulpes vulpes"),
        export_row(2, taxon_species_name="Vulpes vulpes"),
    ]).to_csv(up, index=False)
    pd.DataFrame([export_row(2), export_row(3)]).to_csv(lp, index=False)
    monkeypatch.setattr(etl, "RAW_PATH_UP", up)
    monkeypatch.setattr(etl, "RAW_PATH_LP", lp)
    monkeypatch.setattr(etl, "PROCESSED_PATH", output)

    etl.main()

    result = pd.read_parquet(output)
    assert result["observation_id"].tolist() == [1, 2, 3]
    summary = summarize_species(result)
    assert summary["scientific_name"].tolist() == ["Vulpes vulpes"]
    assert summary["observed_count"].tolist() == [3]


def test_invalid_rows_are_filtered():
    rows = [export_row(), export_row(), export_row(2, latitude=91),
            export_row(3, observed_on="invalid"), export_row(4, scientific_name=" "),
            export_row(5, iconic_taxon_name="Arachnida"), export_row(None)]
    result = etl.prepare_historical_observations(pd.DataFrame(rows))
    assert result["observation_id"].tolist() == [1]


def test_missing_name_column_reports_file(tmp_path):
    path = tmp_path / "missing_name.csv"
    pd.DataFrame([export_row()]).drop(columns="scientific_name").to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing_name.csv.*scientific_name"):
        etl.load_historical_export(path)


def test_legacy_export_without_scientific_name(tmp_path):
    path = tmp_path / "legacy.csv"
    pd.DataFrame([export_row(taxon_species_name="Vulpes vulpes")]).drop(
        columns="scientific_name"
    ).to_csv(path, index=False)
    assert etl.load_historical_export(path)["scientific_name"].tolist() == ["Vulpes vulpes"]


def test_recent_observations_preserve_scientific_names():
    result = normalize_recent_observations([{
        "id": 1, "observed_on": "2020-09-15",
        "geojson": {"coordinates": [-85, 45]},
        "taxon": {"name": "Vulpes vulpes", "iconic_taxon_name": "Mammalia"},
    }])
    assert summarize_species(result)["scientific_name"].tolist() == ["Vulpes vulpes"]
    assert normalize_recent_observations([]).empty
