# mypy: ignore-errors
"""Analysis-specific ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.domain.analytics.models import MultiCityQuery


@dataclass
class WindAnalysisResult:
    """Result of wind analysis."""

    windy_days_count: int
    total_days: int
    windy_percentage: float
    max_wind_speed: float
    max_wind_date: str | None
    avg_wind_speed: float
    data: list[dict[str, Any]]
    threshold: float


class WindAnalysisPort(Protocol):
    """Port for wind analysis operations."""

    WINDY_DAY_THRESHOLD_KMH: float = 50.0

    def analyze_wind_data(  # noqa: D102
        self,
        weather_data: dict[str, Any],
        threshold_kmh: float = 50.0,
    ) -> WindAnalysisResult: ...

    def detect_windy_days(  # noqa: D102
        self,
        wind_speeds: list[float],
        dates: list[str],
        threshold_kmh: float = 50.0,
    ) -> list[dict[str, Any]]: ...

    def calculate_wind_statistics(  # noqa: D102
        self,
        wind_speeds: list[float],
    ) -> dict[str, float]: ...


def get_wind_analysis_port() -> WindAnalysisPort:
    """Factory function to get the wind analysis implementation."""
    from src.analytics import wind_analysis  # noqa: PLC0415

    return wind_analysis


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection."""

    anomalies: list[dict[str, Any]]
    total_records: int
    anomaly_count: int
    anomaly_percentage: float
    severity_distribution: dict[str, int]


class AnomalyDetectionPort(Protocol):
    """Port for anomaly detection operations."""

    def detect_anomalies(  # noqa: D102
        self,
        weather_data: dict[str, Any],
        thresholds: dict[str, Any],
    ) -> AnomalyDetectionResult: ...

    def classify_severity(  # noqa: D102
        self,
        value: float,
        _expected_range: tuple,
    ) -> str: ...

    def calculate_z_score(  # noqa: D102
        self,
        value: float,
        mean: float,
        _std_dev: float,
    ) -> float: ...


class AnalyticsQueryPort(Protocol):
    """Port for analytics query building."""

    def create_query(  # noqa: D102
        self,
        query_type: str,
        region: str,
        date: str,
        limit: int | None = None,
        _extra_params: dict[str, Any] | None = None,
    ) -> MultiCityQuery: ...

    def validate_query(self, query: MultiCityQuery) -> bool: ...  # noqa: D102


class QueryTypeConfigPort(Protocol):
    """Port for query type configuration."""

    def get_query_types(self) -> dict[str, dict[str, Any]]: ...  # noqa: D102
    def get_query_type(self, query_type: str) -> dict[str, Any] | None: ...  # noqa: D102
    def get_metric_for_query_type(self, query_type: str) -> str: ...  # noqa: D102
    def get_unit_for_query_type(self, query_type: str) -> str: ...  # noqa: D102
