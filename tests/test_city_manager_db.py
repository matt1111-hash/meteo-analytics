"""CityManagerDB osztály tesztjei."""

from __future__ import annotations

from src.data.city_manager_db import CityManagerDB


class TestModuleStructure:
    """Modul struktúra tesztek."""

    def test_city_manager_db_class_exists(self) -> None:
        """A CityManagerDB osztály létezik."""
        assert CityManagerDB is not None

    def test_has_required_attributes(self) -> None:
        """A CityManagerDB rendelkezik a kötelező attribútumokkal."""
        assert hasattr(CityManagerDB, "__init__")
        assert hasattr(CityManagerDB, "close")
        assert hasattr(CityManagerDB, "_execute_query")
        assert hasattr(CityManagerDB, "_initialize_databases")
        assert hasattr(CityManagerDB, "_validate_database_structure")
        assert hasattr(CityManagerDB, "_validate_hungarian_database_structure")

    def test_has_all_export(self) -> None:
        """A modul rendelkezik __all__-lal."""
        from src.data.city_manager_db import __all__  # noqa: PLC0415

        assert __all__ == ["CityManagerDB"]

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        from src.data.city_manager_db import __doc__  # noqa: PLC0415

        assert __doc__ is not None
        assert len(__doc__) > 0
