#!/usr/bin/env python3
"""
Open-Meteo Provider Implementation
Global Weather Analyzer project

Part of the weather_client refactoring - split into focused modules.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import requests

from src.config import APIConfig

from .weather_provider_base import WeatherProvider
from .weather_types import WeatherAPIError

logger = logging.getLogger(__name__)


class OpenMeteoProvider(WeatherProvider):
    """
    Open-Meteo API provider with batching logic for multi-year support.

    Handles requests to Open-Meteo API with automatic batching
    for time periods longer than 90 days.
    """

    def __init__(self):
        """Initialize Open-Meteo provider."""
        super().__init__("open-meteo", "Open-Meteo API")
        self.base_url = APIConfig.OPEN_METEO_ARCHIVE
        self.session.headers.update({
            "User-Agent": APIConfig.USER_AGENT,
            "Accept": "application/json"
        })

        # Batching configuration for rate limit optimization
        self.max_days_per_request = 90
        self.batch_delay = 0.6

        logger.info(f"OpenMeteoProvider - max days/request: {self.max_days_per_request}")

    def validate_provider(self) -> bool:
        """Open-Meteo is always available (no API key needed)."""
        return True

    def get_weather_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get weather data with smart batching.

        Automatically batches requests for periods > 90 days.
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days_diff = (end_dt - start_dt).days

        logger.info(f"Open-Meteo query: {days_diff} days ({start_date} → {end_date})")

        if days_diff > self.max_days_per_request:
            logger.info(f"Multi-year batching: {days_diff} days > {self.max_days_per_request} limit")
            return self.get_weather_data_batched(latitude, longitude, start_date, end_date)
        else:
            return self.get_weather_data_single(latitude, longitude, start_date, end_date)

    def get_weather_data_single(self, latitude: float, longitude: float,
                               start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Single Open-Meteo API request (max 90 days)."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "windspeed_10m_max",
                "wind_gusts_10m_max",
                "winddirection_10m_dominant"
            ],
            "timezone": "auto",
            "models": "era5_seamless"
        }

        return self._make_api_request(params)

    def get_weather_data_batched(self, latitude: float, longitude: float,
                                start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Multi-year query with batching logic."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = (end_dt - start_dt).days

        logger.info(f"Batching start: {total_days} days")

        batches = self._generate_batches(start_dt, end_dt)
        logger.info(f"Generated batches: {len(batches)}")

        all_weather_data = []
        successful_batches = 0
        failed_batches = 0

        for i, (batch_start, batch_end) in enumerate(batches, 1):
            batch_start_str = batch_start.strftime("%Y-%m-%d")
            batch_end_str = batch_end.strftime("%Y-%m-%d")

            try:
                batch_data = self.get_weather_data_single(
                    latitude, longitude, batch_start_str, batch_end_str
                )

                if batch_data:
                    all_weather_data.extend(batch_data)
                    successful_batches += 1

                if i < len(batches):
                    time.sleep(self.batch_delay)

            except WeatherAPIError as e:
                failed_batches += 1
                logger.error(f"Batch {i} error: {e}")
                continue

        all_weather_data.sort(key=lambda x: x.get('date', ''))

        logger.info(f"Batching complete: {successful_batches}/{len(batches)} successful")
        logger.info(f"Total records: {len(all_weather_data)}/{total_days}")

        return all_weather_data

    def _generate_batches(self, start_dt: datetime, end_dt: datetime) -> List[Tuple[datetime, datetime]]:
        """Generate time period batches."""
        batches = []
        current_start = start_dt

        while current_start <= end_dt:
            current_end = min(
                current_start + timedelta(days=self.max_days_per_request - 1),
                end_dt
            )
            batches.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)

        return batches

    def _make_api_request(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute Open-Meteo API request."""
        self._rate_limit_check()

        try:
            response = self.session.get(self.base_url, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
            self._update_request_tracking()

            if response.status_code == 200:
                data = response.json()
                if "daily" not in data:
                    raise WeatherAPIError(f"Invalid response: {data}")
                return self._process_response(data)
            elif response.status_code == 400:
                raise WeatherAPIError(f"Bad request: {response.text}")
            elif response.status_code == 429:
                raise WeatherAPIError("Rate limit exceeded")
            else:
                raise WeatherAPIError(f"API error: {response.status_code}")

        except requests.exceptions.Timeout:
            raise WeatherAPIError("API timeout")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Connection error")

    def _process_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Open-Meteo API response."""
        daily_data = response_data.get("daily", {})
        dates = daily_data.get("time", [])

        if not dates:
            return []

        metrics = {}
        for key, values in daily_data.items():
            if key != "time" and isinstance(values, list):
                metrics[key] = values

        weather_data = []
        for i, date in enumerate(dates):
            daily_record = {"date": date, "data_source": self.provider_id}

            for metric_name, metric_values in metrics.items():
                if i < len(metric_values):
                    daily_record[metric_name] = metric_values[i]

            weather_data.append(daily_record)

        return weather_data


__all__ = ['OpenMeteoProvider']
