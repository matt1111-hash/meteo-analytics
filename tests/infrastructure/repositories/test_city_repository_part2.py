"""Tests split from test_city_repository.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.infrastructure.repositories.test_city_repository_support import *


def test_get_cities_for_region_filters_by_country_codes(tmp_path: Path) -> None:
    """get_cities_for_region filters by provided country codes and applies limit."""
    cities_db = tmp_path / "cities.db"
    create_cities_db(
        cities_db,
        [
            {
                "city": "Munich",
                "country": "Germany",
                "country_code": "DE",
                "lat": 48.1,
                "lon": 11.6,
                "population": 1500000,
                "meteostat_station_id": None,
                "data_quality_score": 0.95,
            },
            {
                "city": "Graz",
                "country": "Austria",
                "country_code": "AT",
                "lat": 47.1,
                "lon": 15.4,
                "population": 300000,
                "meteostat_station_id": None,
                "data_quality_score": 0.9,
            },
            {
                "city": "Linz",
                "country": "Austria",
                "country_code": "AT",
                "lat": 48.3,
                "lon": 14.3,
                "population": 45000,
                "meteostat_station_id": None,
                "data_quality_score": 0.5,
            },
        ],
    )
    repository = build_repository(db_path=cities_db, hungarian_db_path=cities_db)
    results = repository.get_cities_for_region(
        mapped_region="Europe",
        original_region="Europe",
        country_codes=["AT", "DE"],
        limit=2,
        hungarian_mapping={},
    )
    assert [row["city"] for row in results] == ["Munich", "Graz"]
    assert all(row["country_code"] in {"DE", "AT"} for row in results)
