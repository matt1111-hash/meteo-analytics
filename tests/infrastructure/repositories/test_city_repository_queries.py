"""Direct tests for CityRepositoryQueries branch behavior."""

from __future__ import annotations

from pathlib import Path

from src.infrastructure.repositories.city_repository_queries import CityRepositoryQueries

from tests.infrastructure.repositories.test_city_repository_support import (
    create_cities_db,
    create_hungarian_settlements_db,
)


def test_get_cities_by_names_returns_empty_for_no_city_names(tmp_path: Path) -> None:
    """Empty city-name input should short-circuit without queries."""
    queries = CityRepositoryQueries(
        db_path=tmp_path / "cities.db",
        hungarian_db_path=tmp_path / "hungarian.db",
    )

    assert queries.get_cities_by_names([]) == []


def test_get_cities_by_names_falls_back_to_hungarian_database(
    tmp_path: Path,
) -> None:
    """Hungarian settlements should be used when the global DB is missing."""
    hungarian_db = tmp_path / "hungarian.db"
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
            }
        ],
    )
    queries = CityRepositoryQueries(
        db_path=tmp_path / "missing.db",
        hungarian_db_path=hungarian_db,
    )

    results = queries.get_cities_by_names(["Gödöllő"])

    assert results == [
        {
            "city": "Gödöllő",
            "country": "Magyarország",
            "country_code": "HU",
            "lat": 47.6,
            "lon": 19.4,
            "population": 70000,
            "meteostat_station_id": None,
            "data_quality_score": 2.0,
        }
    ]


def test_get_cities_for_region_routes_all_supported_paths(tmp_path: Path) -> None:
    """Region routing should dispatch to global, Hungarian, and country queries."""
    cities_db = tmp_path / "cities.db"
    hungarian_db = tmp_path / "hungarian.db"
    create_cities_db(
        cities_db,
        [
            {
                "city": "Budapest",
                "country": "Hungary",
                "country_code": "HU",
                "lat": 47.5,
                "lon": 19.0,
                "population": 1750000,
                "meteostat_station_id": None,
                "data_quality_score": 1.0,
            },
            {
                "city": "Vienna",
                "country": "Austria",
                "country_code": "AT",
                "lat": 48.2,
                "lon": 16.3,
                "population": 1900000,
                "meteostat_station_id": None,
                "data_quality_score": 0.9,
            },
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
            }
        ],
    )
    queries = CityRepositoryQueries(cities_db, hungarian_db)

    global_results = queries.get_cities_for_region(
        mapped_region="Global",
        original_region="Global",
        country_codes=[],
        limit=1,
        hungarian_mapping={},
    )
    hungarian_results = queries.get_cities_for_region(
        mapped_region="Hungary",
        original_region="Pest",
        country_codes=[],
        limit=1,
        hungarian_mapping={"Pest": ["Pest"]},
    )
    country_results = queries.get_cities_for_region(
        mapped_region="Europe",
        original_region="Europe",
        country_codes=["AT"],
        limit=1,
        hungarian_mapping={},
    )

    assert global_results[0]["city"] == "Vienna"
    assert hungarian_results[0]["city"] == "Gödöllő"
    assert country_results[0]["city"] == "Vienna"


def test_query_hungarian_region_returns_empty_without_mapping(tmp_path: Path) -> None:
    """Region queries without mapped counties should return no rows."""
    queries = CityRepositoryQueries(
        db_path=tmp_path / "cities.db",
        hungarian_db_path=tmp_path / "hungarian.db",
    )

    assert queries.query_hungarian_region("Unknown", {}, 5) == []


def test_autocomplete_city_name_combines_global_and_hungarian_results(
    tmp_path: Path,
) -> None:
    """Autocomplete should merge global and Hungarian matches up to the limit."""
    cities_db = tmp_path / "cities.db"
    hungarian_db = tmp_path / "hungarian.db"
    create_cities_db(
        cities_db,
        [
            {
                "city": "Budapest",
                "country": "Hungary",
                "country_code": "HU",
                "lat": 47.5,
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
                "name": "Budakeszi",
                "megye": "Pest",
                "latitude": 47.5,
                "longitude": 18.9,
                "population": 15000,
                "region_priority": 1.0,
            }
        ],
    )
    queries = CityRepositoryQueries(cities_db, hungarian_db)

    results = queries.autocomplete_city_name("Bud", limit=5)

    assert [result["city"] for result in results] == ["Budapest", "Budakeszi"]


def test_autocomplete_city_name_rejects_short_queries(tmp_path: Path) -> None:
    """Autocomplete should reject too-short query fragments."""
    queries = CityRepositoryQueries(
        db_path=tmp_path / "cities.db",
        hungarian_db_path=tmp_path / "hungarian.db",
    )

    assert queries.autocomplete_city_name("B") == []
