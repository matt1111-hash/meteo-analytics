"""City and weather-related domain ports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from src.domain.value_objects.enums import DataProvider


class CityManagerPort(Protocol):
    """Port for city search and management operations."""

    @property
    def defdb_path(self) -> Path: ...  # noqa: D102

    @property
    def hungarian_db_path(self) -> Path: ...  # noqa: D102

    def find_city_by_name(self, city_name: str) -> tuple | None: ...  # noqa: D102
    def find_cities_by_name(  # noqa: D102
        self, city_name: str, limit: int = 10
    ) -> list[dict[str, Any]]: ...
    def get_city_by_id(self, city_id: int) -> dict[str, Any] | None: ...  # noqa: D102
    def get_cities_in_bounding_box(  # noqa: D102
        self,
        _min_lat: float,
        _max_lat: float,
        _min_lon: float,
        _max_lon: float,
        limit: int = 100,
    ) -> list[dict[str, Any]]: ...
    def get_cities_for_region(  # noqa: D102
        self,
        region: str,
        limit: int | None = None,
        max_cities: int | None = None,
    ) -> list[dict[str, Any]]: ...
    def search_cities(self, query: str, limit: int = 20) -> list[dict[str, Any]]: ...  # noqa: D102
    def get_all_countries(self) -> list[str]: ...  # noqa: D102
    def get_regions_for_country(self, country: str) -> list[str]: ...  # noqa: D102
    def get_hungarian_counties(self) -> list[str]: ...  # noqa: D102
    def get_cities_for_hungarian_county(self, county: str) -> list[dict[str, Any]]: ...  # noqa: D102
    def get_cities_for_hungarian_region(self, region: str) -> list[dict[str, Any]]: ...  # noqa: D102
    def validate_paths(self) -> bool: ...  # noqa: D102
    def close(self) -> None: ...  # noqa: D102


@dataclass
class WeatherFetchParams:
    """Parameters for weather data fetching."""

    latitude: float
    longitude: float
    start_date: str
    end_date: str
    daily_params: list[str]
    hourly_params: list[str] | None = None
    timezone: str = "UTC"
    provider: DataProvider = DataProvider.OPEN_METEO


class WeatherDataProtocol(Protocol):
    """Protocol for weather data response."""

    @property
    def daily(self) -> dict[str, Any]: ...  # noqa: D102

    @property
    def hourly(self) -> dict[str, Any]: ...  # noqa: D102

    @property
    def latitude(self) -> float: ...  # noqa: D102

    @property
    def longitude(self) -> float: ...  # noqa: D102

    @property
    def timezone(self) -> str: ...  # noqa: D102

    @property
    def elevation(self) -> float | None: ...  # noqa: D102

    @property
    def provider(self) -> DataProvider: ...  # noqa: D102


class WeatherClientPort(Protocol):
    """Port for weather data fetching operations."""

    def get_weather_data(  # noqa: D102
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        _daily_params: list[str] | None = None,
        _hourly_params: list[str] | None = None,
        provider: DataProvider | None = None,
    ) -> WeatherDataProtocol | None: ...

    def get_current_weather(  # noqa: D102
        self,
        latitude: float,
        longitude: float,
        provider: DataProvider | None = None,
    ) -> dict[str, Any] | None: ...

    def get_forecast(  # noqa: D102
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        provider: DataProvider | None = None,
    ) -> WeatherDataProtocol | None: ...

    def get_supported_providers(self) -> list[DataProvider]: ...  # noqa: D102
    def is_provider_available(self, provider: DataProvider) -> bool: ...  # noqa: D102


class WeatherRepositoryPort(Protocol):
    """Port for weather data repository operations."""

    def save_weather_data(  # noqa: D102
        self,
        weather_data: dict[str, Any],
        city_data: dict[str, Any],
    ) -> bool: ...

    def get_weather_for_city(  # noqa: D102
        self,
        city_id: int,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]] | None: ...

    def get_weather_for_coordinates(  # noqa: D102
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]] | None: ...

    def delete_old_weather_data(self, _days_old: int) -> int: ...  # noqa: D102
