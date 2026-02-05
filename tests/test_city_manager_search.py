"""CityManagerSearch osztály tesztjei."""

from __future__ import annotations

from src.data.city_manager_hungarian import CityManagerHungarian
from src.data.city_manager_search import CityManagerSearch


class TestModuleStructure:
    """Modul struktúra tesztek."""

    def test_city_manager_search_class_exists(self) -> None:
        """A CityManagerSearch osztály létezik."""
        assert CityManagerSearch is not None

    def test_inherits_from_city_manager_hungarian(self) -> None:
        """A CityManagerSearch a CityManagerHungarian-ból származik."""
        assert issubclass(CityManagerSearch, CityManagerHungarian)

    def test_has_required_methods(self) -> None:
        """A CityManagerSearch rendelkezik a kötelező metódusokkal."""
        assert hasattr(CityManagerSearch, 'find_city_by_name')
        assert hasattr(CityManagerSearch, 'search_unified')
        assert hasattr(CityManagerSearch, 'search_cities')
        assert hasattr(CityManagerSearch, 'get_cities_by_country')

    def test_has_all_export(self) -> None:
        """A modul rendelkezik __all__-lal."""
        from src.data.city_manager_search import __all__
        assert __all__ == ['CityManagerSearch']

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        from src.data.city_manager_search import __doc__
        assert __doc__ is not None
        assert len(__doc__) > 0
