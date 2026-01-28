#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherDataWorker API Builder - Build API requests for different providers.
"""

from typing import Any, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherDataWorker


class APIBuilder:
    """Build API requests for different providers."""

    def __init__(self, worker: 'WeatherDataWorker'):
        """
        Initialize API builder.

        Args:
            worker: WeatherDataWorker instance
        """
        self._worker = worker

    def build_request(self, provider: str) -> Tuple[str, Dict[str, Any]]:
        """
        Build provider-specific API request.

        Args:
            provider: Provider identifier

        Returns:
            (api_url, params) tuple
        """
        if provider == "open-meteo":
            return self.build_openmeteo_request()
        elif provider == "meteostat":
            return self.build_meteostat_request()
        else:
            raise ValueError(f"Ismeretlen provider: {provider}")

    def build_openmeteo_request(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build Open-Meteo API request with wind gusts support.

        Returns:
            (url, params) tuple
        """
        from ...utils import APIConstants

        url = APIConstants.OPEN_METEO_ARCHIVE

        params = {
            "latitude": self._worker.latitude,
            "longitude": self._worker.longitude,
            "start_date": self._worker.start_date,
            "end_date": self._worker.end_date,
            # Daily parameters
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,windspeed_10m_max,winddirection_10m_dominant",
            # Hourly parameters - wind gusts
            "hourly": "wind_gusts_10m,windspeed_10m",
            "timezone": "auto"
        }

        return url, params

    def build_meteostat_request(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build Meteostat API request (future expansion).

        Returns:
            (url, params) tuple
        """
        # PLACEHOLDER - Falls back to Open-Meteo
        return self.build_openmeteo_request()
