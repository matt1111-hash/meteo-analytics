#!/usr/bin/env python3
"""
Tests for src/analytics/__init__.py
Main analytics module exports
"""


class TestAnalyticsInit:
    """Test main analytics module exports."""

    def test_exports_multi_city_engine(self) -> None:
        """Should export MultiCityEngine."""
        from src.analytics import MultiCityEngine

        assert MultiCityEngine is not None

    def test_exports_multi_city_query(self) -> None:
        """Should export MultiCityQuery."""
        from src.analytics import MultiCityQuery

        assert MultiCityQuery is not None

    def test_all_exports_count(self) -> None:
        """Should have 2 exports."""
        from src.analytics import __all__

        assert len(__all__) == 2

    def test_all_exports_match_expected(self) -> None:
        """__all__ should contain expected exports."""
        from src.analytics import __all__

        expected = ["MultiCityEngine", "MultiCityQuery"]
        for item in expected:
            assert item in __all__, f"Missing in __all__: {item}"

    def test_can_import_engine(self) -> None:
        """Should be able to import MultiCityEngine."""
        from src import analytics

        assert hasattr(analytics, "MultiCityEngine")

    def test_can_import_query(self) -> None:
        """Should be able to import MultiCityQuery."""
        from src import analytics

        assert hasattr(analytics, "MultiCityQuery")


class TestAnalyticsSubmodules:
    """Test analytics submodules are accessible."""

    def test_multi_city_engine_module_accessible(self) -> None:
        """multi_city_engine submodule should be accessible."""
        from src.analytics import multi_city_engine

        assert hasattr(multi_city_engine, "MultiCityEngine")

    def test_multi_city_types_module_accessible(self) -> None:
        """multi_city_types submodule should be accessible."""
        from src.analytics import multi_city_types

        assert hasattr(multi_city_types, "REGIONS")
        assert hasattr(multi_city_types, "HUNGARIAN_REGIONAL_MAPPING")

    def test_multi_city_legacy_module_accessible(self) -> None:
        """multi_city_legacy submodule should be accessible."""
        from src.analytics import multi_city_legacy

        assert hasattr(multi_city_legacy, "safe_mean")
        assert hasattr(multi_city_legacy, "safe_median")

    def test_wind_analysis_module_accessible(self) -> None:
        """wind_analysis submodule should be accessible."""
        from src.analytics import wind_analysis

        assert hasattr(wind_analysis, "analyze_wind_patterns")

    def test_ports_module_accessible(self) -> None:
        """ports submodule should be accessible."""
        from src.analytics import ports

        assert hasattr(ports, "MultiCityEnginePort")
