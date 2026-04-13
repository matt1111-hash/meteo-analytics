#!/usr/bin/env python3
"""
Tests for src/analytics/wind_analysis.py
Wind analysis compatibility wrapper
"""


class TestWindAnalysisImports:
    """Test that wind_analysis properly re-exports domain components."""

    def test_exports_analyze_wind_patterns(self) -> None:
        """Should export analyze_wind_patterns from domain."""
        from src.analytics.wind_analysis import analyze_wind_patterns  # noqa: PLC0415

        assert callable(analyze_wind_patterns)

    def test_exports_extract_daily_wind_data(self) -> None:
        """Should export extract_daily_wind_data from domain."""
        from src.analytics.wind_analysis import extract_daily_wind_data  # noqa: PLC0415

        assert callable(extract_daily_wind_data)

    def test_exports_identify_windy_days(self) -> None:
        """Should export identify_windy_days from domain."""
        from src.analytics.wind_analysis import identify_windy_days  # noqa: PLC0415

        assert callable(identify_windy_days)

    def test_exports_months_hu(self) -> None:
        """Should export MONTHS_HU constant."""
        from src.analytics.wind_analysis import MONTHS_HU  # noqa: PLC0415

        assert isinstance(MONTHS_HU, list)

    def test_exports_windy_day_threshold(self) -> None:
        """Should export WINDY_DAY_THRESHOLD_KMH constant."""
        from src.analytics.wind_analysis import WINDY_DAY_THRESHOLD_KMH  # noqa: PLC0415

        assert isinstance(WINDY_DAY_THRESHOLD_KMH, (int, float))
        assert WINDY_DAY_THRESHOLD_KMH > 0

    def test_exports_wind_analysis_result(self) -> None:
        """Should export WindAnalysisResult dataclass."""
        from src.analytics.wind_analysis import WindAnalysisResult  # noqa: PLC0415

        # Check it's a class that can be instantiated
        assert WindAnalysisResult is not None

    def test_exports_wind_chart_data(self) -> None:
        """Should export WindChartData dataclass."""
        from src.analytics.wind_analysis import WindChartData  # noqa: PLC0415

        assert WindChartData is not None

    def test_exports_windy_day_stats(self) -> None:
        """Should export WindyDayStats dataclass."""
        from src.analytics.wind_analysis import WindyDayStats  # noqa: PLC0415

        assert WindyDayStats is not None

    def test_exports_format_wind_analysis_summary(self) -> None:
        """Should export format_wind_analysis_summary function."""
        from src.analytics.wind_analysis import format_wind_analysis_summary  # noqa: PLC0415

        assert callable(format_wind_analysis_summary)

    def test_exports_get_chart_data_for_monthly_windy_days(self) -> None:
        """Should export get_chart_data_for_monthly_windy_days function."""
        from src.analytics.wind_analysis import (  # noqa: PLC0415
            get_chart_data_for_monthly_windy_days,
        )

        assert callable(get_chart_data_for_monthly_windy_days)

    def test_exports_calculate_monthly_windy_stats(self) -> None:
        """Should export calculate_monthly_windy_stats function."""
        from src.analytics.wind_analysis import calculate_monthly_windy_stats  # noqa: PLC0415

        assert callable(calculate_monthly_windy_stats)


class TestWindAnalysisAllExports:
    """Test __all__ exports."""

    def test_all_exports_count(self) -> None:
        """Should have correct number of exports."""
        from src.analytics import wind_analysis  # noqa: PLC0415

        assert len(wind_analysis.__all__) == 11

    def test_all_exports_accessible(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import wind_analysis  # noqa: PLC0415

        for name in wind_analysis.__all__:
            assert hasattr(wind_analysis, name), f"Missing export: {name}"

    def test_all_exports_match_expected(self) -> None:
        """__all__ should contain expected exports."""
        from src.analytics import wind_analysis  # noqa: PLC0415

        expected = [
            "MONTHS_HU",
            "WINDY_DAY_THRESHOLD_KMH",
            "WindAnalysisResult",
            "WindChartData",
            "WindyDayStats",
            "analyze_wind_patterns",
            "calculate_monthly_windy_stats",
            "extract_daily_wind_data",
            "format_wind_analysis_summary",
            "get_chart_data_for_monthly_windy_days",
            "identify_windy_days",
        ]
        for item in expected:
            assert item in wind_analysis.__all__, f"Missing in __all__: {item}"


class TestMonthHuConstant:
    """Test MONTHS_HU constant."""

    def test_months_hu_has_12_entries(self) -> None:
        """MONTHS_HU should have 12 month entries."""
        from src.analytics.wind_analysis import MONTHS_HU  # noqa: PLC0415

        assert len(MONTHS_HU) == 12

    def test_months_hu_is_list_of_strings(self) -> None:
        """MONTHS_HU should be a list of month name strings."""
        from src.analytics.wind_analysis import MONTHS_HU  # noqa: PLC0415

        for month in MONTHS_HU:
            assert isinstance(month, str), f"Month {month} is not a string"

    def test_months_hu_values_are_hungarian(self) -> None:
        """MONTHS_HU should contain Hungarian month names."""
        from src.analytics.wind_analysis import MONTHS_HU  # noqa: PLC0415

        # Check some Hungarian month names
        hungarian_months = [
            "Január",
            "Február",
            "Március",
            "Április",
            "Május",
            "Június",
            "Július",
            "Augusztus",
            "Szeptember",
            "Október",
            "November",
            "December",
        ]
        for month in hungarian_months:
            assert month in MONTHS_HU, f"Missing Hungarian month: {month}"


class TestWindyDayThreshold:
    """Test WINDY_DAY_THRESHOLD_KMH constant."""

    def test_threshold_is_positive(self) -> None:
        """Threshold should be positive."""
        from src.analytics.wind_analysis import WINDY_DAY_THRESHOLD_KMH  # noqa: PLC0415

        assert WINDY_DAY_THRESHOLD_KMH > 0

    def test_threshold_is_reasonable(self) -> None:
        """Threshold should be in reasonable range for windy days."""
        from src.analytics.wind_analysis import WINDY_DAY_THRESHOLD_KMH  # noqa: PLC0415

        # Typical windy day threshold is around 50 km/h
        assert 30 <= WINDY_DAY_THRESHOLD_KMH <= 100
