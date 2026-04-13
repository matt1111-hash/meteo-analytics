#!/usr/bin/env python3
"""
Tests for src/domain/analytics/wind_models.py
Wind analysis models and constants
"""

import datetime

from src.domain.analytics.wind_models import (
    MONTHS_HU,
    WINDY_DAY_THRESHOLD_KMH,
    WindAnalysisResult,
    WindChartData,
    WindyDayStats,
)


class TestConstants:
    """Test wind model constants."""

    def test_windy_day_threshold_is_positive(self) -> None:
        """WINDY_DAY_THRESHOLD_KMH should be positive."""
        assert WINDY_DAY_THRESHOLD_KMH > 0

    def test_windy_day_threshold_is_reasonable(self) -> None:
        """WINDY_DAY_THRESHOLD_KMH should be in reasonable range."""
        # Typical windy day threshold is 40-50 km/h
        assert 30 <= WINDY_DAY_THRESHOLD_KMH <= 60

    def test_months_hu_has_12_entries(self) -> None:
        """MONTHS_HU should have 12 entries."""
        assert len(MONTHS_HU) == 12

    def test_months_hu_are_hungarian(self) -> None:
        """MONTHS_HU should contain Hungarian month names."""
        expected = [
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
        assert expected == MONTHS_HU

    def test_months_hu_are_strings(self) -> None:
        """MONTHS_HU entries should be strings."""
        assert all(isinstance(m, str) for m in MONTHS_HU)


class TestWindyDayStats:
    """Test WindyDayStats dataclass."""

    def test_creates_with_all_fields(self) -> None:
        """Should create with all fields."""
        stat = WindyDayStats(
            year=2026,
            month=2,
            month_name="Február",
            windy_days_count=5,
            total_days=28,
            windy_percentage=17.86,
            max_wind_speed=80.0,
            avg_wind_speed=45.0,
            windy_days_list=[datetime.date(2026, 2, 1), datetime.date(2026, 2, 5)],
        )
        assert stat.year == 2026
        assert stat.month == 2
        assert stat.windy_days_count == 5

    def test_is_dataclass(self) -> None:
        """Should be a dataclass."""
        import dataclasses  # noqa: PLC0415

        assert dataclasses.is_dataclass(WindyDayStats)

    def test_field_types(self) -> None:
        """Should have correct field types."""
        stat = WindyDayStats(
            year=2026,
            month=2,
            month_name="Február",
            windy_days_count=5,
            total_days=28,
            windy_percentage=17.86,
            max_wind_speed=80.0,
            avg_wind_speed=45.0,
            windy_days_list=[],
        )
        assert isinstance(stat.year, int)
        assert isinstance(stat.month, int)
        assert isinstance(stat.month_name, str)
        assert isinstance(stat.windy_days_count, int)
        assert isinstance(stat.total_days, int)
        assert isinstance(stat.windy_percentage, float)
        assert isinstance(stat.max_wind_speed, float)
        assert isinstance(stat.avg_wind_speed, float)
        assert isinstance(stat.windy_days_list, list)


class TestWindAnalysisResult:
    """Test WindAnalysisResult dataclass."""

    def test_creates_with_all_fields(self) -> None:
        """Should create with all fields."""
        monthly_stat = WindyDayStats(
            year=2026,
            month=2,
            month_name="Február",
            windy_days_count=5,
            total_days=28,
            windy_percentage=17.86,
            max_wind_speed=80.0,
            avg_wind_speed=45.0,
            windy_days_list=[],
        )
        result = WindAnalysisResult(
            location_name="Budapest",
            analysis_period=(datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)),
            threshold_kmh=50.0,
            monthly_stats=[monthly_stat],
            total_windy_days=30,
            total_days=365,
            overall_windy_percentage=8.2,
            windiest_month=monthly_stat,
            calmest_month=monthly_stat,
        )
        assert result.location_name == "Budapest"
        assert result.threshold_kmh == 50.0
        assert result.total_windy_days == 30

    def test_is_dataclass(self) -> None:
        """Should be a dataclass."""
        import dataclasses  # noqa: PLC0415

        assert dataclasses.is_dataclass(WindAnalysisResult)

    def test_optional_fields_can_be_none(self) -> None:
        """Optional fields should accept None."""
        result = WindAnalysisResult(
            location_name="Test",
            analysis_period=(datetime.date(2026, 1, 1), datetime.date(2026, 1, 31)),
            threshold_kmh=50.0,
            monthly_stats=[],
            total_windy_days=0,
            total_days=31,
            overall_windy_percentage=0.0,
            windiest_month=None,
            calmest_month=None,
        )
        assert result.windiest_month is None
        assert result.calmest_month is None


class TestWindChartData:
    """Test WindChartData TypedDict."""

    def test_accepts_correct_structure(self) -> None:
        """Should accept correct structure."""
        data: WindChartData = {
            "months": ["Január", "Február"],
            "counts": [5, 3],
            "percentages": [16.1, 10.7],
            "labels": ["Jan: 5", "Feb: 3"],
        }
        assert data["months"] == ["Január", "Február"]
        assert data["counts"] == [5, 3]

    def test_is_typed_dict(self) -> None:
        """Should be a TypedDict."""
        assert issubclass(WindChartData, dict)
