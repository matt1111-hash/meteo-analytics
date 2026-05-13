#!/usr/bin/env python3
"""
Meteostat Provider Implementation
Global Weather Analyzer project

Part of the weather_client refactoring - split into focused modules.
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any

import requests
from src.config import APIConfig

from .weather_provider_base import WeatherProvider
from .weather_types import ProviderValidationError, WeatherAPIError

logger = logging.getLogger(__name__)


class MeteostatProvider(WeatherProvider):
    """
    Meteostat API provider with multi-year support.

    Supports up to 10 years per request with automatic batching.
    """

    def __init__(self):
        """Initialize Meteostat provider."""
        super().__init__("meteostat", "Meteostat API")
        self.base_url = APIConfig.METEOSTAT_BASE
        self.api_key = os.getenv("METEOSTAT_API_KEY")

        if self.api_key:
            self.session.headers.update(
                {
                    "User-Agent": APIConfig.USER_AGENT,
                    "Accept": "application/json",
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": "meteostat.p.rapidapi.com",
                }
            )

        self.min_request_interval = APIConfig.METEOSTAT_RATE_LIMIT
        self.max_years_per_request = 10

        logger.info(f"MeteostatProvider - max {self.max_years_per_request} years/request")

    def validate_provider(self) -> bool:
        """Validate Meteostat API key."""
        return bool(self.api_key and len(self.api_key.strip()) >= 32)  # noqa: PLR2004

    def get_weather_data(
        self, latitude: float, longitude: float, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """
        Get weather data with smart dispatch.

        Uses batching for periods > 10 years.
        """
        if not self.validate_provider():
            raise ProviderValidationError("Meteostat API key missing or invalid")

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        years_diff = (end_dt - start_dt).days / 365.25

        logger.info(f"Meteostat query: {years_diff:.1f} years")

        if years_diff > self.max_years_per_request:
            return self.get_weather_data_batched(latitude, longitude, start_date, end_date)
        else:
            return self.get_weather_data_single(latitude, longitude, start_date, end_date)

    def get_weather_data_single(
        self, latitude: float, longitude: float, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """Single Meteostat API request."""
        params = {
            "lat": latitude,
            "lon": longitude,
            "start": start_date,
            "end": end_date,
        }

        return self._make_api_request(params)

    def get_weather_data_batched(
        self, latitude: float, longitude: float, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """Multi-year query with batching logic."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        batches = []
        current_start = start_dt

        while current_start <= end_dt:
            current_end = min(
                current_start.replace(year=current_start.year + self.max_years_per_request),
                end_dt,
            )
            batches.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)

        logger.info(f"Meteostat batches: {len(batches)}")

        all_data = []
        for i, (batch_start, batch_end) in enumerate(batches, 1):
            try:
                batch_start_str = batch_start.strftime("%Y-%m-%d")
                batch_end_str = batch_end.strftime("%Y-%m-%d")

                batch_data = self.get_weather_data_single(
                    latitude, longitude, batch_start_str, batch_end_str
                )

                if batch_data:
                    all_data.extend(batch_data)

                if i < len(batches):
                    time.sleep(self.min_request_interval)

            except Exception as e:
                logger.error(f"Meteostat batch {i} error: {e}")
                continue

        return sorted(all_data, key=lambda x: x.get("date", ""))

    def _make_api_request(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute Meteostat API request."""
        self._rate_limit_check()

        endpoint = f"{self.base_url}/point/daily"

        try:
            response = self.session.get(endpoint, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
            self._update_request_tracking()

            if response.status_code == 200:  # noqa: PLR2004
                data = response.json()
                if "data" not in data:
                    raise WeatherAPIError(f"Invalid response: {data}")
                return self._process_response(data)
            elif response.status_code == 401:  # noqa: PLR2004
                raise ProviderValidationError("Authentication error")
            elif response.status_code == 429:  # noqa: PLR2004
                raise WeatherAPIError("Rate limit exceeded")
            else:
                raise WeatherAPIError(f"API error: {response.status_code}")

        except requests.exceptions.Timeout:
            raise WeatherAPIError("API timeout")  # noqa: B904
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Connection error")  # noqa: B904

    def _process_response(self, response_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Process Meteostat API response."""
        raw_data = response_data.get("data", [])

        if not raw_data:
            return []

        field_mapping = {
            "date": "date",
            "tavg": "temperature_2m_mean",
            "tmin": "temperature_2m_min",
            "tmax": "temperature_2m_max",
            "prcp": "precipitation_sum",
            "wspd": "windspeed_10m_max",
            "wpgt": "wind_gusts_10m_max",
            "wdir": "winddirection_10m_dominant",
            "tsun": "sunshine_duration",
        }

        weather_data = []
        for record in raw_data:
            daily_record = {"data_source": self.provider_id}

            for meteostat_field, openmeteo_field in field_mapping.items():
                if meteostat_field in record:
                    value = record[meteostat_field]
                    daily_record[openmeteo_field] = value

            if "temperature_2m_max" in daily_record:
                daily_record["apparent_temperature_max"] = daily_record["temperature_2m_max"]
            if "temperature_2m_min" in daily_record:
                daily_record["apparent_temperature_min"] = daily_record["temperature_2m_min"]

            weather_data.append(daily_record)

        return weather_data


__all__ = ["MeteostatProvider"]
