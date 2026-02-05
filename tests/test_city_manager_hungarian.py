"""CityManagerHungarian osztály tesztjei."""

from __future__ import annotations

from src.data.city_manager_db import CityManagerDB
from src.data.city_manager_hungarian import CityManagerHungarian


class TestModuleStructure:
    """Modul struktúra tesztek."""

    def test_city_manager_hungarian_class_exists(self) -> None:
        """A CityManagerHungarian osztály létezik."""
        assert CityManagerHungarian is not None

    def test_inherits_from_city_manager_db(self) -> None:
        """A CityManagerHungarian a CityManagerDB-ból származik."""
        assert issubclass(CityManagerHungarian, CityManagerDB)

    def test_has_required_methods(self) -> None:
        """A CityManagerHungarian rendelkezik a kötelező metódusokkal."""
        assert hasattr(CityManagerHungarian, 'search_hungarian_settlements')
        assert hasattr(CityManagerHungarian, 'get_hungarian_counties')
        assert hasattr(CityManagerHungarian, 'get_hungarian_settlement_types')
        assert hasattr(CityManagerHungarian, 'get_hungarian_settlements_by_county')

    def test_has_all_export(self) -> None:
        """A modul rendelkezik __all__-lal."""
        from src.data.city_manager_hungarian import __all__
        assert __all__ == ['CityManagerHungarian']

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        from src.data.city_manager_hungarian import __doc__
        assert __doc__ is not None
        assert len(__doc__) > 0
