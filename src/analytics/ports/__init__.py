#!/usr/bin/env python3
"""
Analytics Ports - Analytics Layer Ports (Abstractions)

Clean Architecture Ports for Analytics Layer implementations.

These ports define the interfaces that Analytics Layer implementations must satisfy.
This allows the outer layers (API, Presentation) to depend on abstractions
rather than concrete implementations.

Ports:
    - MultiCityEnginePort: Multi-city analytics operations
    - WindAnalysisPort: Wind analysis operations
    - AnomalyDetectionPort: Anomaly detection operations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from src.domain.analytics.models import MultiCityQuery
from src.domain.entities.analytics_models import (
    AnalyticsQuestion,
    AnalyticsResult,
)
from src.domain.ports import (
    CityRepositoryPort,
    WeatherClientPort,
)

# =============================================================================
# Multi-City Engine Port
# =============================================================================

class MultiCityEnginePort(Protocol):
    """
    Port for multi-city analytics operations.

    This protocol defines the interface for multi-city weather analytics.
    Implementations should handle:
    - Query execution for multiple cities
    - Region-based filtering
    - Result transformation and sorting
    - Progress tracking
    """

    def analyze_multi_city(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: Optional[int] = None,
        question: Optional[AnalyticsQuestion] = None,
    ) -> AnalyticsResult: ...

    def execute_analytics_query(
        self,
        query: MultiCityQuery,
        progress_callback: Optional[callable] = None,
    ) -> AnalyticsResult: ...

    def get_cities_for_region(
        self,
        region: str,
        limit: Optional[int] = None,
        max_cities: Optional[int] = None,
    ) -> List[Dict[str, Any]]: ...

    def resolve_region_name(self, region_input: str) -> str: ...


@dataclass
class MultiCityEngineConfig:
    """Configuration for MultiCityEngine."""
    max_workers: int = 8
    request_timeout: int = 90
    max_retries: int = 2
    retry_delay: float = 3.0


def get_multi_city_engine_port(
    city_repository: Optional[CityRepositoryPort] = None,
    weather_client: Optional[WeatherClientPort] = None,
    config: Optional[MultiCityEngineConfig] = None,
) -> MultiCityEnginePort:
    """
    Factory function to get MultiCityEnginePort implementation.

    Args:
        city_repository: Optional city repository port
        weather_client: Optional weather client port
        config: Optional engine configuration

    Returns:
        MultiCityEnginePort implementation
    """
    from pathlib import Path

    from src.analytics.multi_city_engine_core import MultiCityEngine

    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "cities.db"
    hungarian_db_path = project_root / "data" / "hungarian_settlements.db"

    return MultiCityEngine(
        db_path=str(db_path),
        hungarian_db_path=str(hungarian_db_path),
        city_repository=city_repository,
    )


# =============================================================================
# Wind Analysis Port
# =============================================================================

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
    """
    Port for wind analysis operations.

    This protocol defines the interface for wind data analysis.
    Implementations should handle:
    - Windy day detection
    - Wind speed statistics
    - Threshold-based classification
    """

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
    """
    Factory function to get WindAnalysisPort implementation.

    Returns:
        WindAnalysisPort implementation
    """
    from src.analytics import wind_analysis
    return wind_analysis


# =============================================================================
# Anomaly Detection Port
# =============================================================================

@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection."""
    anomalies: List[Dict[str, Any]]
    total_records: int
    anomaly_count: int
    anomaly_percentage: float
    severity_distribution: Dict[str, int]


class AnomalyDetectionPort(Protocol):
    """
    Port for anomaly detection operations.

    This protocol defines the interface for weather anomaly detection.
    Implementations should handle:
    - Threshold-based anomaly detection
    - Severity classification
    - Statistical outlier detection
    """

    def detect_anomalies(
        self,
        weather_data: Dict[str, Any],
        thresholds: Dict[str, Any],
    ) -> AnomalyDetectionResult: ...

    def classify_severity(
        self,
        value: float,
        expected_range: tuple,
    ) -> str: ...

    def calculate_z_score(
        self,
        value: float,
        mean: float,
        std_dev: float,
    ) -> float: ...


# =============================================================================
# Analytics Query Port
# =============================================================================

class AnalyticsQueryPort(Protocol):
    """
    Port for analytics query building.

    This protocol defines the interface for creating and validating
    analytics queries.
    """

    def create_query(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> MultiCityQuery: ...

    def validate_query(self, query: MultiCityQuery) -> bool: ...


# =============================================================================
# Query Type Configuration Port
# =============================================================================

class QueryTypeConfigPort(Protocol):
    """
    Port for query type configuration.

    This protocol defines the interface for query type metadata.
    """

    def get_query_types(self) -> Dict[str, Dict[str, Any]]: ...
    def get_query_type(self, query_type: str) -> Optional[Dict[str, Any]]: ...
    def get_metric_for_query_type(self, query_type: str) -> str: ...
    def get_unit_for_query_type(self, query_type: str) -> str: ...
