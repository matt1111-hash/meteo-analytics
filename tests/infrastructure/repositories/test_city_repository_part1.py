"""Tests split from test_city_repository.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.infrastructure.repositories.test_city_repository_support import *


def test_validate_paths_raises_when_both_databases_missing(tmp_path: Path) -> None:
    """validate_paths raises when neither database exists."""
    repository = build_repository(
        db_path=tmp_path / "cities.db", hungarian_db_path=tmp_path / "hungarian.db"
    )
    repository.db_path = tmp_path / "missing.db"
    repository.hungarian_db_path = tmp_path / "missing_hungarian.db"
    with pytest.raises(RuntimeError, match="No databases available"):
        repository.validate_paths()


def test_validate_paths_logs_warning_when_only_hungarian_db_missing(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """validate_paths logs warnings but does not raise when one database exists."""
    cities_path = tmp_path / "cities.db"
    cities_path.touch()
    repository = build_repository(db_path=cities_path, hungarian_db_path=tmp_path / "hungarian.db")
    repository.hungarian_db_path = tmp_path / "missing_hungarian.db"
    with caplog.at_level("WARNING"):
        repository.validate_paths()
    assert "Hungarian settlements database missing" in caplog.text


def test_get_cities_for_region_global_limits_and_sorts_by_population(
    tmp_path: Path,
) -> None:
    """get_cities_for_region returns the most populous global cities first."""
    cities_db = tmp_path / "cities.db"
    create_cities_db(
        cities_db,
        [
            {
                "city": "CityA",
                "country": "A",
                "country_code": "AA",
                "lat": 1.0,
                "lon": 2.0,
                "population": 150000,
                "meteostat_station_id": None,
                "data_quality_score": 0.9,
            },
            {
                "city": "CityB",
                "country": "B",
                "country_code": "BB",
                "lat": 3.0,
                "lon": 4.0,
                "population": 220000,
                "meteostat_station_id": None,
                "data_quality_score": 0.8,
            },
        ],
    )
    repository = build_repository(db_path=cities_db, hungarian_db_path=cities_db)
    results = repository.get_cities_for_region(
        mapped_region="Global",
        original_region="Global",
        country_codes=[],
        limit=1,
        hungarian_mapping={},
    )
    assert len(results) == 1
    assert results[0]["city"] == "CityB"


def test_get_cities_for_region_uses_hungarian_mapping(tmp_path: Path) -> None:
    """get_cities_for_region returns settlements filtered by Hungarian counties."""
    cities_db = tmp_path / "cities.db"
    hungarian_db = tmp_path / "hungarian.db"
    create_cities_db(
        cities_db,
        [
            {
                "city": "Budapest",
                "country": "Hungary",
                "country_code": "HU",
                "lat": 47.0,
                "lon": 19.0,
                "population": 1750000,
                "meteostat_station_id": None,
                "data_quality_score": 1.0,
            }
        ],
    )
    create_hungarian_settlements_db(
        hungarian_db,
        [
            {
                "name": "Gödöllő",
                "megye": "Pest",
                "latitude": 47.6,
                "longitude": 19.4,
                "population": 70000,
                "region_priority": 2.0,
            },
            {
                "name": "Vác",
                "megye": "Pest",
                "latitude": 47.8,
                "longitude": 19.1,
                "population": 35000,
                "region_priority": 1.0,
            },
        ],
    )
    repository = build_repository(db_path=cities_db, hungarian_db_path=hungarian_db)
    mapping: Dict[str, List[str]] = {"Pest": ["Pest"]}
    results = repository.get_cities_for_region(
        mapped_region="Hungary",
        original_region="Pest",
        country_codes=[],
        limit=2,
        hungarian_mapping=mapping,
    )
    assert [row["city"] for row in results] == ["Gödöllő", "Vác"]
    assert all(row["country_code"] == "HU" for row in results)


def test_get_cities_for_region_returns_hungary_all_when_mapping_missing(
    tmp_path: Path,
) -> None:
    """get_cities_for_region falls back to full Hungary query when mapping is absent."""
    cities_db = tmp_path / "cities.db"
    create_cities_db(
        cities_db,
        [
            {
                "city": "Debrecen",
                "country": "Hungary",
                "country_code": "HU",
                "lat": 47.5,
                "lon": 21.6,
                "population": 200000,
                "meteostat_station_id": None,
                "data_quality_score": 0.9,
            },
            {
                "city": "Szeged",
                "country": "Hungary",
                "country_code": "HU",
                "lat": 46.3,
                "lon": 20.1,
                "population": 160000,
                "meteostat_station_id": None,
                "data_quality_score": 0.8,
            },
        ],
    )
    repository = build_repository(db_path=cities_db, hungarian_db_path=cities_db)
    results = repository.get_cities_for_region(
        mapped_region="Hungary",
        original_region="Unknown",
        country_codes=[],
        limit=1,
        hungarian_mapping={},
    )
    assert len(results) == 1
    assert results[0]["city"] == "Debrecen"
