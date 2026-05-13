"""CityManager class hierarchy tests."""

from __future__ import annotations

from src.infrastructure.city_manager import (
    city_manager_db,
    city_manager_hungarian,
    city_manager_search,
    city_manager_stats,
)


class TestClassHierarchy:
    """Osztály hierarchia tesztek."""

    def test_city_manager_hungarian_inherits_from_db(self) -> None:
        """A CityManagerHungarian a CityManagerDB-ból származik."""
        assert issubclass(
            city_manager_hungarian.CityManagerHungarian, city_manager_db.CityManagerDB
        )

    def test_city_manager_search_inherits_from_hungarian(self) -> None:
        """A CityManagerSearch a CityManagerHungarian-ból származik."""
        assert issubclass(
            city_manager_search.CityManagerSearch,
            city_manager_hungarian.CityManagerHungarian,
        )

    def test_city_manager_stats_inherits_from_search(self) -> None:
        """A CityManagerStats a CityManagerSearch-ből származik."""
        assert issubclass(
            city_manager_stats.CityManagerStats, city_manager_search.CityManagerSearch
        )

    def test_city_manager_inherits_from_all_parents(self) -> None:
        """A CityManager (CityManagerStats) az összes szülőből származik."""
        assert issubclass(
            city_manager_stats.CityManagerStats, city_manager_search.CityManagerSearch
        )
        assert issubclass(
            city_manager_stats.CityManagerStats,
            city_manager_hungarian.CityManagerHungarian,
        )
        assert issubclass(city_manager_stats.CityManagerStats, city_manager_db.CityManagerDB)
