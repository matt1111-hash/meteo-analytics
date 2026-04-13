"""Tests split from test_city_manager_hungarian.py."""

from __future__ import annotations

from src.data.city_manager_hungarian import CityManagerHungarian

# ruff: noqa: F403, F405
from tests.data.test_city_manager_hungarian_support import *


class TestGetHungarianSettlementTypes:
    """Test get_hungarian_settlement_types method."""

    def test_returns_list_of_types(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlement_types returns list of settlement types."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        types = manager.get_hungarian_settlement_types()

        assert isinstance(types, list)
        assert "város" in types
        assert "község" in types
        assert "főváros" in types

    def test_returns_sorted_list(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlement_types returns sorted list."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        types = manager.get_hungarian_settlement_types()

        assert types == sorted(types)

    def test_returns_empty_list_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_hungarian_settlement_types returns empty list when DB unavailable."""
        manager = CityManagerHungarian(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        types = manager.get_hungarian_settlement_types()

        assert types == []

    def test_returns_empty_list_for_empty_database(
        self, cities_db: Path, empty_hungarian_db: Path
    ) -> None:
        """get_hungarian_settlement_types returns empty list for empty database."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=empty_hungarian_db)

        types = manager.get_hungarian_settlement_types()

        assert types == []


class TestGetHungarianSettlementsByCounty:
    """Test get_hungarian_settlements_by_county method."""

    def test_returns_settlements_by_county(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlements_by_county returns settlements in county."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("Bács-Kiskun")

        assert len(results) >= 3
        for city in results:
            assert city.megye == "Bács-Kiskun"
            assert city.is_hungarian is True

    def test_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlements_by_county respects limit parameter."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("Bács-Kiskun", limit=3)

        assert len(results) == 3

    def test_returns_empty_list_when_no_match(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlements_by_county returns empty list for unknown county."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("NonExistentCounty")

        assert results == []

    def test_returns_empty_list_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_hungarian_settlements_by_county returns empty list when DB unavailable."""
        manager = CityManagerHungarian(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        results = manager.get_hungarian_settlements_by_county("Budapest")

        assert results == []

    def test_sorted_by_priority_and_population(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlements_by_county sorts by priority then population."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("Bács-Kiskun", limit=10)

        # First result should be Kecskemét (highest priority + population)
        assert results[0].city == "Kecskemét"

    def test_increments_hungarian_query_count(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_settlements_by_county increments hungarian_query_count."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)
        initial_count = manager.hungarian_query_count

        manager.get_hungarian_settlements_by_county("Bács-Kiskun")

        assert manager.hungarian_query_count == initial_count + 1


class TestCityManagerHungarianInheritance:
    """Test CityManagerHungarian inherits from CityManagerDB."""

    def test_has_connection_attribute(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerHungarian has connection attribute from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "connection")
        assert manager.connection is not None

    def test_has_hungarian_connection_attribute(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerHungarian has hungarian_connection attribute from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "hungarian_connection")
        assert manager.hungarian_connection is not None

    def test_has_query_count_attributes(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerHungarian has query count attributes from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "query_count")
        assert hasattr(manager, "hungarian_query_count")

    def test_has_execute_query_method(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerHungarian has _execute_query method from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "_execute_query")
        assert callable(manager._execute_query)

    def test_has_close_method(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerHungarian has close method from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "close")
        assert callable(manager.close)
