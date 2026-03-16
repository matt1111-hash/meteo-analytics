"""Tests split from test_city_manager_stats.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_city_manager_stats_support import *


class TestGetCitiesByContinent:
    """Test get_cities_by_continent method."""

    def test_returns_cities_for_europe(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent returns European cities."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("Europe")

        assert len(results) >= 1
        for city in results:
            assert city.continent == "Europe"

    def test_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_by_continent respects limit."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("Europe", limit=2)

        assert len(results) <= 2

    def test_with_min_population_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent filters by min_population."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("Europe", min_population=1000000)

        for city in results:
            if city.population:
                assert city.population >= 1000000

    def test_returns_empty_for_unknown_continent(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent returns empty for unknown continent."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("NonExistentContinent")

        assert results == []

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent returns empty when global DB unavailable."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        results = manager.get_cities_by_continent("Europe")

        assert results == []


class TestGetAvailableContinents:
    """Test _get_available_continents method."""

    def test_returns_list_of_continents(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_continents returns list of continents."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        continents = manager._get_available_continents()

        assert isinstance(continents, list)
        assert "Europe" in continents
        assert "Asia" in continents

    def test_returns_sorted_list(self, cities_db: Path, hungarian_db: Path) -> None:
        """_get_available_continents returns sorted list."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        continents = manager._get_available_continents()

        assert continents == sorted(continents)

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_get_available_continents returns empty when no connection."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        continents = manager._get_available_continents()

        assert continents == []


class TestGetAvailableCountries:
    """Test _get_available_countries method."""

    def test_returns_list_of_countries(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries returns list of country dicts."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        countries = manager._get_available_countries()

        assert isinstance(countries, list)
        assert len(countries) >= 1

    def test_country_dicts_have_required_fields(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries returns dicts with required fields."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        countries = manager._get_available_countries()

        for country in countries:
            assert "country_code" in country
            assert "country_name" in country
            assert "city_count" in country

    def test_sorted_by_city_count(self, cities_db: Path, hungarian_db: Path) -> None:
        """_get_available_countries sorts by city count descending."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        countries = manager._get_available_countries()

        city_counts = [c["city_count"] for c in countries]
        assert city_counts == sorted(city_counts, reverse=True)

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries returns empty when no connection."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        countries = manager._get_available_countries()

        assert countries == []


class TestContextManager:
    """Test context manager functionality."""

    def test_enter_returns_self(self, cities_db: Path, hungarian_db: Path) -> None:
        """__enter__ returns self."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        with manager as ctx_manager:
            assert ctx_manager is manager

    def test_exit_closes_connections(self, cities_db: Path, hungarian_db: Path) -> None:
        """__exit__ closes database connections."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.connection is not None
        assert manager.hungarian_connection is not None

        with manager:
            pass

        assert manager.connection is None
        assert manager.hungarian_connection is None

    def test_context_manager_with_exception(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Context manager closes connections even with exception."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        try:
            with manager:
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert manager.connection is None
