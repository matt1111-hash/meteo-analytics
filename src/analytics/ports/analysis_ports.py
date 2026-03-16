# mypy: ignore-errors
"""Analysis-specific ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from src.domain.analytics.models import MultiCityQuery


@dataclass
class WindAnalysisResult:
    """Result of wind analysis."""

    windy_days_count: int
    total_days: int
    windy_percentage: float
    max_wind_speed: float
    max_wind_date: Optional[str]
    avg_wind_speed: float
    data: List[Dict[str, Any]]
    threshold: float


class WindAnalysisPort(Protocol):
    """Port for wind analysis operations."""

    WINDY_DAY_THRESHOLD_KMH: float = 50.0

    def analyze_wind_data(
        self,
        weather_data: Dict[str, Any],
        threshold_kmh: float = 50.0,
    ) -> WindAnalysisResult: ...

    def detect_windy_days(
        self,
        wind_speeds: List[float],
        dates: List[str],
        threshold_kmh: float = 50.0,
    ) -> List[Dict[str, Any]]: ...

    def calculate_wind_statistics(
        self,
        wind_speeds: List[float],
    ) -> Dict[str, float]: ...


def get_wind_analysis_port() -> WindAnalysisPort:
    """Factory function to get the wind analysis implementation."""
    from src.analytics import wind_analysis

    return wind_analysis


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection."""

    anomalies: List[Dict[str, Any]]
    total_records: int
    anomaly_count: int
    anomaly_percentage: float
    severity_distribution: Dict[str, int]


class AnomalyDetectionPort(Protocol):
    """Port for anomaly detection operations."""

    def detect_anomalies(
        self,
        weather_data: Dict[str, Any],
        thresholds: Dict[str, Any],
    ) -> AnomalyDetectionResult: ...

    def classify_severity(
        self,
        value: float,
        _expected_range: tuple,
    ) -> str: ...

    def calculate_z_score(
        self,
        value: float,
        mean: float,
        _std_dev: float,
    ) -> float: ...


class AnalyticsQueryPort(Protocol):
    """Port for analytics query building."""

    def create_query(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: Optional[int] = None,
        _extra_params: Optional[Dict[str, Any]] = None,
    ) -> MultiCityQuery: ...

    def validate_query(self, query: MultiCityQuery) -> bool: ...


class QueryTypeConfigPort(Protocol):
    """Port for query type configuration."""

    def get_query_types(self) -> Dict[str, Dict[str, Any]]: ...
    def get_query_type(self, query_type: str) -> Optional[Dict[str, Any]]: ...
    def get_metric_for_query_type(self, query_type: str) -> str: ...
    def get_unit_for_query_type(self, query_type: str) -> str: ...
