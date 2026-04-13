#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_engine.py
Re-exports and backward compatibility tests
"""


class TestMultiCityEngineModule:
    """Test multi_city_engine module re-exports."""

    def test_exports_multi_city_engine(self) -> None:
        """Should export MultiCityEngine from core."""
        from src.analytics.multi_city_engine import MultiCityEngine

        assert MultiCityEngine is not None

    def test_exports_types(self) -> None:
        """Should export type aliases."""
        from src.analytics.multi_city_engine import Number, NumberOrNone

        assert Number is not None
        assert NumberOrNone is not None

    def test_exports_constants(self) -> None:
        """Should export constants."""
        from src.analytics.multi_city_engine import (
            HUNGARIAN_REGIONAL_MAPPING,
            REGIONS,
        )

        assert isinstance(HUNGARIAN_REGIONAL_MAPPING, dict)
        assert isinstance(REGIONS, dict)

    def test_exports_legacy_functions(self) -> None:
        """Should export legacy wrapper functions."""
        from src.analytics.multi_city_engine import (
            safe_mean,
            safe_median,
            safe_min_max,
            safe_statistics_mean,
            safe_statistics_median,
            safe_statistics_stdev,
            safe_stdev,
        )

        assert callable(safe_mean)
        assert callable(safe_median)
        assert callable(safe_min_max)
        assert callable(safe_statistics_mean)
        assert callable(safe_statistics_median)
        assert callable(safe_statistics_stdev)
        assert callable(safe_stdev)

    def test_exports_demo_function(self) -> None:
        """Should export demo function."""
        from src.analytics.multi_city_engine import demo_multi_city_engine

        assert callable(demo_multi_city_engine)


class TestMultiCityEngineAllExports:
    """Test __all__ exports."""

    def test_all_exports_count(self) -> None:
        """Should have correct number of exports."""
        from src.analytics import multi_city_engine

        assert len(multi_city_engine.__all__) == 13

    def test_all_exports_accessible(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import multi_city_engine

        for name in multi_city_engine.__all__:
            assert hasattr(multi_city_engine, name), f"Missing export: {name}"

    def test_all_exports_match_expected(self) -> None:
        """__all__ should contain expected exports."""
        from src.analytics import multi_city_engine

        expected = [
            "Number",
            "NumberOrNone",
            "HUNGARIAN_REGIONAL_MAPPING",
            "REGIONS",
            "safe_mean",
            "safe_statistics_mean",
            "safe_median",
            "safe_statistics_median",
            "safe_stdev",
            "safe_statistics_stdev",
            "safe_min_max",
            "MultiCityEngine",
            "demo_multi_city_engine",
        ]
        for item in expected:
            assert item in multi_city_engine.__all__, f"Missing in __all__: {item}"


class TestLegacyFunctionDelegation:
    """Test that legacy functions delegate to domain layer."""

    def test_safe_mean_delegates_correctly(self) -> None:
        """safe_mean should produce same result as domain layer."""
        from src.analytics.multi_city_engine import safe_mean

        result = safe_mean([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_safe_median_delegates_correctly(self) -> None:
        """safe_median should produce same result as domain layer."""
        from src.analytics.multi_city_engine import safe_median

        result = safe_median([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_safe_stdev_delegates_correctly(self) -> None:
        """safe_stdev should produce same result as domain layer."""
        from src.analytics.multi_city_engine import safe_stdev

        result = safe_stdev([2, 4, 4, 4, 5, 5, 7, 9])
        assert result is not None
        assert abs(result - 2.138) < 0.01

    def test_safe_min_max_delegates_correctly(self) -> None:
        """safe_min_max should produce same result as domain layer."""
        from src.analytics.multi_city_engine import safe_min_max

        result = safe_min_max([3, 1, 4, 1, 5, 9, 2, 6])
        assert result == (1.0, 9.0)


class TestQueryTypesAccessibility:
    """Test QUERY_TYPES is accessible from engine class."""

    def test_query_types_accessible_from_class(self) -> None:
        """QUERY_TYPES should be accessible from MultiCityEngine class."""
        from src.analytics.multi_city_engine import MultiCityEngine

        assert hasattr(MultiCityEngine, "QUERY_TYPES")
        assert isinstance(MultiCityEngine.QUERY_TYPES, dict)

    def test_query_types_has_expected_keys(self) -> None:
        """QUERY_TYPES should have expected query type keys."""
        from src.analytics.multi_city_engine import MultiCityEngine

        expected_keys = [
            "hottest_today",
            "coldest_today",
            "temperature_mean",
            "wettest_today",
            "windiest_today",
        ]
        for key in expected_keys:
            assert key in MultiCityEngine.QUERY_TYPES, f"Missing query type: {key}"
