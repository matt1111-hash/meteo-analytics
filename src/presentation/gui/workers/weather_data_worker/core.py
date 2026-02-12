#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherDataWorker Core - Main WeatherDataWorker class.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    pass

from ..base_worker import BaseWorkerThread
from .api_builder import APIBuilder
from .api_executor import APIExecutor
from .executor import WorkerExecutor
from .wind_validator import WindValidator


class WeatherDataWorker(BaseWorkerThread):
    """
    🔧 Weather data worker with cancellation support.
    🌪️ WIND GUSTS + 🌍 PROVIDER ROUTING.

    ÚJ FUNKCIÓK:
    ✅ Teljes cancellation support minden HTTP request-nél
    ✅ Explicit completion_signal UI auto-hide-hoz
    ✅ Comprehensive progress tracking
    ✅ Provider fallback cancellation support
    """

    # Specifikus signalok
    weather_data_completed = Signal(dict)

    # Provider routing signalok
    provider_changed = Signal(str)
    provider_fallback_occurred = Signal(str, str)
    provider_validation_failed = Signal(str, str)

    def __init__(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        preferred_provider: str = "auto",
        parent: Optional["QObject"] = None,
    ):
        """
        Initialize WeatherDataWorker.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date string
            end_date: End date string
            preferred_provider: Preferred data provider
            parent: Parent QObject
        """
        super().__init__(parent)

        self.latitude = latitude
        self.longitude = longitude
        self.start_date = start_date
        self.end_date = end_date
        self.preferred_provider = preferred_provider
        self.actual_provider: Optional[str] = None
        self.weather_data: Optional[Dict[str, Any]] = None

        # Helper components
        self._executor = WorkerExecutor(self)
        self._api_builder = APIBuilder(self)
        self._api_executor = APIExecutor(self)
        self._wind_validator = WindValidator(self)

        print(f"🌍 DEBUG: WeatherDataWorker created - {preferred_provider} provider")

    def execute(self) -> None:
        """Execute weather data fetch."""
        self._executor.execute()

    def _select_optimal_provider(self) -> Optional[str]:
        """Select optimal provider."""
        return self._executor._select_optimal_provider()

    def _build_api_request(self, provider: str):
        """Build API request for provider."""
        return self._api_builder.build_request(provider)

    def _build_openmeteo_request(self):
        """Build Open-Meteo API request."""
        return self._api_builder.build_openmeteo_request()

    def _build_meteostat_request(self):
        """Build Meteostat API request."""
        return self._api_builder.build_meteostat_request()

    def _execute_api_request(
        self, provider: str, api_url: str, params: Dict[str, Any]
    ) -> bool:
        """Execute API request."""
        return self._api_executor.execute_request(provider, api_url, params)

    def _get_provider_headers(self, provider: str) -> Dict[str, str]:
        """Get provider headers."""
        return self._api_executor.get_provider_headers(provider)

    def _validate_wind_gusts_data(self) -> None:
        """Validate wind gusts data."""
        self._wind_validator.validate()
