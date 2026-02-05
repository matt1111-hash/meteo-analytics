"""city_manager_demo tesztjei."""

from __future__ import annotations

from src.data.city_manager_demo import demo_dual_database_city_manager


class TestModuleStructure:
    """Modul struktúra tesztek."""

    def test_demo_function_exists(self) -> None:
        """A demo függvény létezik."""
        assert demo_dual_database_city_manager is not None
        assert callable(demo_dual_database_city_manager)

    def test_demo_function_has_docstring(self) -> None:
        """A demo függvény rendelkezik dokumentációval."""
        assert demo_dual_database_city_manager.__doc__ is not None
        assert len(demo_dual_database_city_manager.__doc__) > 0

    def test_has_all_export(self) -> None:
        """A modul rendelkezik __all__-lal."""
        from src.data.city_manager_demo import __all__
        assert __all__ == ['demo_dual_database_city_manager']

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        from src.data.city_manager_demo import __doc__
        assert __doc__ is not None
        assert len(__doc__) > 0
