"""City and weather-related domain ports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from src.domain.value_objects.enums import DataProvider


class CityManagerPort(Protocol):
    """Port for city search and management operations."""

    @property
    def defdb_path(self) -> Path: ...

    @property
    def hungarian_db_path(self) -> Path: ...

    def find_city_by_name(self, city_name: str) -> Optional[tuple]: ...
    def find_cities_by_name(
        self, city_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]: ...
    def get_city_by_id(self, city_id: int) -> Optional[Dict[str, Any]]: ...
    def get_cities_in_bounding_box(
        self,
        _min_lat: float,
        _max_lat: float,
        _min_lon: float,
        _max_lon: float,
        limit: int = 100,
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


@dataclass
class WeatherFetchParams:
    """Parameters for weather data fetching."""

    latitude: float
    longitude: float
    start_date: str
    end_date: str
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
    """Port for weather data fetching operations."""

    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        _daily_params: Optional[List[str]] = None,
        _hourly_params: Optional[List[str]] = None,
        provider: Optional[DataProvider] = None,
    ) -> Optional[WeatherDataProtocol]: ...

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        provider: Optional[DataProvider] = None,
    ) -> Optional[Dict[str, Any]]: ...

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        provider: Optional[DataProvider] = None,
    ) -> Optional[WeatherDataProtocol]: ...

    def get_supported_providers(self) -> List[DataProvider]: ...
    def is_provider_available(self, provider: DataProvider) -> bool: ...


class WeatherRepositoryPort(Protocol):
    """Port for weather data repository operations."""

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

    def delete_old_weather_data(self, _days_old: int) -> int: ...
