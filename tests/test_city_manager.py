"""city_manager re-export modul tesztjei."""

from __future__ import annotations

from src.data import city_manager
from src.infrastructure.city_manager import (
    city_manager_db,
    city_manager_demo,
    city_manager_hungarian,
    city_manager_search,
    city_manager_stats,
)


class TestCityManagerReexports:
    """Teszteli, hogy a city_manager.py modul helyesen re-exportálja az összes komponenst."""

    def test_reexports_types(self) -> None:
        """A city_types modul összes típusa elérhető."""
        assert hasattr(city_manager, "RegionType")
        assert hasattr(city_manager, "CitySort")
        assert hasattr(city_manager, "City")
        assert hasattr(city_manager, "CityQuery")
        assert hasattr(city_manager, "CityDatabaseError")

    def test_reexports_main_class(self) -> None:
        """A fő CityManager (CityManagerStats) elérhető."""
        assert hasattr(city_manager, "CityManager")
        assert city_manager.CityManager is city_manager_stats.CityManagerStats

    def test_reexports_individual_classes(self) -> None:
        """Az egyedi osztályok elérhetőek."""
        assert hasattr(city_manager, "CityManagerDB")
        assert hasattr(city_manager, "CityManagerHungarian")
        assert hasattr(city_manager, "CityManagerSearch")
        assert hasattr(city_manager, "CityManagerStats")

        assert city_manager.CityManagerDB is city_manager_db.CityManagerDB
        assert city_manager.CityManagerHungarian is city_manager_hungarian.CityManagerHungarian
        assert city_manager.CityManagerSearch is city_manager_search.CityManagerSearch
        assert city_manager.CityManagerStats is city_manager_stats.CityManagerStats

    def test_reexports_demo_function(self) -> None:
        """A demo függvény elérhető."""
        assert hasattr(city_manager, "demo_dual_database_city_manager")
        assert (
            city_manager.demo_dual_database_city_manager
            is city_manager_demo.demo_dual_database_city_manager
        )

    def test_all_exports_defined(self) -> None:
        """A __all__ lista tartalmazza az összes exportot."""
        expected_all = {
            "RegionType",
            "CitySort",
            "City",
            "CityQuery",
            "CityDatabaseError",
            "CityManager",
            "CityManagerDB",
            "CityManagerHungarian",
            "CityManagerSearch",
            "CityManagerStats",
            "demo_dual_database_city_manager",
        }
        actual_all = set(city_manager.__all__)
        assert actual_all == expected_all

    def test_all_exports_actually_exist(self) -> None:
        """A __all__-ban felsorolt exportok tényleg léteznek."""
        for name in city_manager.__all__:
            assert hasattr(city_manager, name), f"Missing export: {name}"

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        assert city_manager.__doc__ is not None
        assert len(city_manager.__doc__) > 0

    def test_module_structure_matches_documentation(self) -> None:
        """A modul dokumentációja alapján ellenőrizzük a struktúrát."""
        doc = city_manager.__doc__
        assert "city_types.py" in doc
        assert "city_manager_db.py" in doc
        assert "city_manager_hungarian.py" in doc
        assert "city_manager_search.py" in doc
        assert "city_manager_stats.py" in doc
        assert "city_manager_demo.py" in doc


class TestBackwardCompatibility:
    """Teszteli a visszafelé kompatibilitást."""

    def test_legacy_import_pattern_works(self) -> None:
        """A dokumentációban leírt legacy import működik."""
        from src.data.city_manager import City, CityDatabaseError, CityManager  # noqa: PLC0415

        assert CityManager is not None
        assert CityDatabaseError is not None
        assert City is not None

    def test_recommended_import_pattern_works(self) -> None:
        """A dokumentációban javasolt új import minta működik."""
        from src.infrastructure.city_manager.city_manager_stats import (  # noqa: PLC0415
            CityManagerStats as CityManager,
        )
        from src.infrastructure.city_manager.city_types import (  # noqa: PLC0415
            City,
            CityDatabaseError,
        )

        assert CityManager is not None
        assert City is not None
        assert CityDatabaseError is not None

    def test_both_imports_reference_same_class(self) -> None:
        """A CityManager mindkét import módszerrel ugyanazt az osztályt adja."""
        from src.data.city_manager import CityManager as LegacyCityManager  # noqa: PLC0415
        from src.infrastructure.city_manager.city_manager_stats import (  # noqa: PLC0415
            CityManagerStats,
        )

        assert LegacyCityManager is CityManagerStats


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
        assert issubclass(city_manager.CityManager, city_manager_search.CityManagerSearch)
        assert issubclass(city_manager.CityManager, city_manager_hungarian.CityManagerHungarian)
        assert issubclass(city_manager.CityManager, city_manager_db.CityManagerDB)
