#!/usr/bin/env python3
"""
Domain Ports - Data Layer Ports (Abstractions)

Clean Architecture Ports for Data Layer implementations.

These ports define the interfaces that Data Layer implementations must satisfy.
This allows the inner layers (Domain, Application) to depend on abstractions
rather than concrete implementations.

Ports:
    - CityManagerPort: City search and management operations
    - WeatherClientPort: Weather data fetching operations
    - CityRepositoryPort: City data repository operations
    - WeatherRepositoryPort: Weather data repository operations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from src.domain.value_objects.enums import (
    AnalyticsMetric,
    DataProvider,
    DataSource,
    RegionScope,
)
from src.domain.value_objects.enums import QuestionType as DomainQuestionType

# =============================================================================
# City Manager Port
# =============================================================================

class CityManagerPort(Protocol):
    """
    Port for city search and management operations.

    This protocol defines the interface for city-related operations.
    Implementations should handle:
    - City search (global and Hungarian-specific)
    - City retrieval by name, coordinates, or ID
    - Database queries with filtering and sorting
    """

    @property
    def defdb_path(self) -> Path: ...
    @property
    def hungarian_db_path(self) -> Path: ...

    def find_city_by_name(self, city_name: str) -> Optional[tuple]: ...
    def find_cities_by_name(self, city_name: str, limit: int = 10) -> List[Dict[str, Any]]: ...
    def get_city_by_id(self, city_id: int) -> Optional[Dict[str, Any]]: ...
    def get_cities_in_bounding_box(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        limit: int = 100
    ) -> List[Dict[str, Any]]: ...
    def get_cities_for_region(
        self,
        region: str,
        limit: Optional[int] = None,
        max_cities: Optional[int] = None,
    ) -> List[Dict[str, Any]]: ...
    def search_cities(self, query: str, limit: int = 20) -> List[Dict[str, Any]]: ...
    def get_all_countries(self) -> List[str]: ...
    def get_regions_for_country(self, country: str) -> List[str]: ...
    def get_hungarian_counties(self) -> List[str]: ...
    def get_cities_for_hungarian_county(self, county: str) -> List[Dict[str, Any]]: ...
    def get_cities_for_hungarian_region(self, region: str) -> List[Dict[str, Any]]: ...
    def validate_paths(self) -> bool: ...
    def close(self) -> None: ...


# =============================================================================
# Weather Client Port
# =============================================================================

@dataclass
class WeatherFetchParams:
    """Parameters for weather data fetching."""
    latitude: float
    longitude: float
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    daily_params: List[str]
    hourly_params: Optional[List[str]] = None
    timezone: str = "UTC"
    provider: DataProvider = DataProvider.OPEN_METEO


class WeatherDataProtocol(Protocol):
    """Protocol for weather data response."""
    @property
    def daily(self) -> Dict[str, Any]: ...
    @property
    def hourly(self) -> Dict[str, Any]: ...
    @property
    def latitude(self) -> float: ...
    @property
    def longitude(self) -> float: ...
    @property
    def timezone(self) -> str: ...
    @property
    def elevation(self) -> Optional[float]: ...
    @property
    def provider(self) -> DataProvider: ...


class WeatherClientPort(Protocol):
    """
    Port for weather data fetching operations.

    This protocol defines the interface for weather API operations.
    Implementations should handle:
    - Fetching weather data from various providers
    - Provider fallback and selection
    - Error handling and retries
    """

    def get_weather_data(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        daily_params: Optional[List[str]] = None,
        hourly_params: Optional[List[str]] = None,
        provider: Optional[DataProvider] = None,
    ) -> Optional[WeatherDataProtocol]: ...

    def get_current_weather(
        self,
        lat: float,
        lon: float,
        provider: Optional[DataProvider] = None,
    ) -> Optional[Dict[str, Any]]: ...

    def get_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 7,
        provider: Optional[DataProvider] = None,
    ) -> Optional[WeatherDataProtocol]: ...

    def get_supported_providers(self) -> List[DataProvider]: ...
    def is_provider_available(self, provider: DataProvider) -> bool: ...


# =============================================================================
# City Repository Port
# =============================================================================

class CityRepositoryPort(Protocol):
    """
    Port for city data repository operations.

    This protocol defines the interface for city data storage operations.
    Implementations should handle:
    - CRUD operations for cities
    - Region-based queries
    - Filtering and sorting
    """

    @property
    def db_path(self) -> Path: ...
    @property
    def hungarian_db_path(self) -> Path: ...

    def validate_paths(self) -> bool: ...
    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: List[str],
        limit: int,
        hungarian_mapping: Dict[str, str],
    ) -> List[Dict[str, Any]]: ...
    def search_cities(self, query: str, limit: int = 20) -> List[Dict[str, Any]]: ...
    def get_city_by_id(self, city_id: int) -> Optional[Dict[str, Any]]: ...
    def get_city_by_coordinates(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[Dict[str, Any]]: ...
    def close(self) -> None: ...


# =============================================================================
# Weather Repository Port
# =============================================================================

class WeatherRepositoryPort(Protocol):
    """
    Port for weather data repository operations.

    This protocol defines the interface for weather data storage operations.
    Implementations should handle:
    - Storing weather data
    - Retrieving historical weather data
    - Querying by date range and location
    """

    def save_weather_data(
        self,
        weather_data: Dict[str, Any],
        city_data: Dict[str, Any],
    ) -> bool: ...

    def get_weather_for_city(
        self,
        city_id: int,
        start_date: date,
        end_date: date,
    ) -> Optional[List[Dict[str, Any]]]: ...

    def get_weather_for_coordinates(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> Optional[List[Dict[str, Any]]]: ...

    def delete_old_weather_data(self, days_old: int) -> int: ...


# =============================================================================
# Analytics Metric Port
# =============================================================================

class AnalyticsMetricPort(Protocol):
    """
    Port for analytics metric operations.

    This protocol defines the interface for metric-related operations.
    """

    @staticmethod
    def get_metric_enum(value: str) -> AnalyticsMetric: ...
    @staticmethod
    def get_metric_display_name(metric: AnalyticsMetric) -> str: ...
    @staticmethod
    def get_metric_unit(metric: AnalyticsMetric) -> str: ...
    @staticmethod
    def validate_metric(metric: AnalyticsMetric) -> bool: ...


# =============================================================================
# Anomaly Profile Port
# =============================================================================

class AnomalyProfilePort(Protocol):
    """
    Port for anomaly profile management operations.

    This protocol defines the interface for anomaly profile operations.
    """

    def get_active_profile(self) -> Dict[str, Any]: ...
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]: ...
    def get_all_profiles(self) -> List[Dict[str, Any]]: ...
    def create_profile(self, name: str, data: Dict[str, Any]) -> bool: ...
    def update_profile(self, name: str, data: Dict[str, Any]) -> bool: ...
    def delete_profile(self, name: str) -> bool: ...


# =============================================================================
# Question Type Port
# =============================================================================

class QuestionTypePort(Protocol):
    """
    Port for question type operations.

    This protocol defines the interface for question type-related operations.
    """

    @staticmethod
    def get_question_type_enum(value: str) -> DomainQuestionType: ...
    @staticmethod
    def get_question_type_display_name(question_type: DomainQuestionType) -> str: ...
    @staticmethod
    def get_available_metrics_for_question_type(
        question_type: DomainQuestionType,
    ) -> List[AnalyticsMetric]: ...


# =============================================================================
# Data Source Port
# =============================================================================

class DataSourcePort(Protocol):
    """
    Port for data source operations.

    This protocol defines the interface for data source-related operations.
    """

    @staticmethod
    def get_data_source_enum(value: str) -> DataSource: ...
    @staticmethod
    def get_data_source_display_name(source: DataSource) -> str: ...


# =============================================================================
# Region Scope Port
# =============================================================================

class RegionScopePort(Protocol):
    """
    Port for region scope operations.

    This protocol defines the interface for region scope-related operations.
    """

    @staticmethod
    def get_region_scope_enum(value: str) -> RegionScope: ...
    @staticmethod
    def get_region_scope_display_name(scope: RegionScope) -> str: ...
    @staticmethod
    def validate_region_scope(scope: RegionScope) -> bool: ...


# =============================================================================
# Factory Functions for Port Instantiation
# =============================================================================

def get_city_manager_port() -> CityManagerPort:
    """
    Factory function to get CityManagerPort implementation.

    Returns:
        CityManagerPort implementation from Data Layer
    """
    from src.data.city_manager_stats import CityManagerStats
    return CityManagerStats()


def get_weather_client_port() -> WeatherClientPort:
    """
    Factory function to get WeatherClientPort implementation.

    Returns:
        WeatherClientPort implementation from Data Layer
    """
    from src.data.weather_client_extensions import WeatherClientExtensions
    return WeatherClientExtensions()


def get_city_repository_port() -> CityRepositoryPort:
    """
    Factory function to get CityRepositoryPort implementation.

    Returns:
        CityRepositoryPort implementation from Infrastructure Layer
    """
    from pathlib import Path

    from src.infrastructure.repositories.city_repository import CityRepository

    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "cities.db"
    hungarian_db_path = project_root / "data" / "hungarian_settlements.db"

    return CityRepository(db_path, hungarian_db_path)
