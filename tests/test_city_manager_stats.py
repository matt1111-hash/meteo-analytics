"""CityManagerStats osztály tesztjei."""

from __future__ import annotations

from src.data.city_manager_search import CityManagerSearch
from src.data.city_manager_stats import CityManagerStats


class TestModuleStructure:
    """Modul struktúra tesztek."""

    def test_city_manager_stats_class_exists(self) -> None:
        """A CityManagerStats osztály létezik."""
        assert CityManagerStats is not None

    def test_inherits_from_city_manager_search(self) -> None:
        """A CityManagerStats a CityManagerSearch-ből származik."""
        assert issubclass(CityManagerStats, CityManagerSearch)

    def test_has_required_methods(self) -> None:
        """A CityManagerStats rendelkezik a kötelező metódusokkal."""
        assert hasattr(CityManagerStats, 'get_database_statistics')
        assert hasattr(CityManagerStats, 'get_hungarian_statistics')
        assert hasattr(CityManagerStats, 'get_cities_by_continent')
        assert hasattr(CityManagerStats, '__enter__')
        assert hasattr(CityManagerStats, '__exit__')

    def test_has_context_manager_support(self) -> None:
        """A CityManagerStats támogatja a context managert."""
        assert hasattr(CityManagerStats, '__enter__')
        assert hasattr(CityManagerStats, '__exit__')

    def test_has_all_export(self) -> None:
        """A modul rendelkezik __all__-lal."""
        from src.data.city_manager_stats import __all__
        assert __all__ == ['CityManagerStats']

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        from src.data.city_manager_stats import __doc__
        assert __doc__ is not None
        assert len(__doc__) > 0
