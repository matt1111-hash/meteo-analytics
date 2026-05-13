#!/usr/bin/env python3
"""
Tests for src/analytics/__init__.py
Main analytics module exports
"""


class TestAnalyticsInit:
    """Test main analytics module exports."""

    def test_exports_multi_city_engine(self) -> None:
        """Should export MultiCityEngine."""
        from src.analytics import MultiCityEngine  # noqa: PLC0415

        assert MultiCityEngine is not None

    def test_exports_multi_city_query(self) -> None:
        """Should export MultiCityQuery."""
        from src.analytics import MultiCityQuery  # noqa: PLC0415

        assert MultiCityQuery is not None

    def test_all_exports_count(self) -> None:
        """Should have 2 exports."""
        from src.analytics import __all__  # noqa: PLC0415

        assert len(__all__) == 2

    def test_all_exports_match_expected(self) -> None:
        """__all__ should contain expected exports."""
        from src.analytics import __all__  # noqa: PLC0415

        expected = ["MultiCityEngine", "MultiCityQuery"]
        for item in expected:
            assert item in __all__, f"Missing in __all__: {item}"

    def test_can_import_engine(self) -> None:
        """Should be able to import MultiCityEngine."""
        from src import analytics  # noqa: PLC0415

        assert hasattr(analytics, "MultiCityEngine")

    def test_can_import_query(self) -> None:
        """Should be able to import MultiCityQuery."""
        from src import analytics  # noqa: PLC0415

        assert hasattr(analytics, "MultiCityQuery")


class TestAnalyticsSubmodules:
    """Test analytics submodules are accessible."""

    def test_multi_city_engine_module_accessible(self) -> None:
        """multi_city_engine submodule should be accessible."""
        from src.analytics import multi_city_engine  # noqa: PLC0415

        assert hasattr(multi_city_engine, "MultiCityEngine")

    def test_multi_city_types_module_accessible(self) -> None:
        """multi_city_engine now re-exports types from domain."""
        from src.analytics import multi_city_engine  # noqa: PLC0415

        assert hasattr(multi_city_engine, "REGIONS")
        assert hasattr(multi_city_engine, "HUNGARIAN_REGIONAL_MAPPING")

    def test_multi_city_legacy_module_accessible(self) -> None:
        """multi_city_engine now re-exports legacy statistics from domain."""
        from src.analytics import multi_city_engine  # noqa: PLC0415

        assert hasattr(multi_city_engine, "safe_mean")
        assert hasattr(multi_city_engine, "safe_median")

    def test_wind_analysis_module_accessible(self) -> None:
        """wind_analysis submodule should be accessible."""
        from src.analytics import wind_analysis  # noqa: PLC0415

        assert hasattr(wind_analysis, "analyze_wind_patterns")

    def test_ports_module_accessible(self) -> None:
        """ports submodule should be accessible."""
        from src.analytics import ports  # noqa: PLC0415

        assert hasattr(ports, "MultiCityEnginePort")
