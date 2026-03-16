#!/usr/bin/env python3
"""Weather client core."""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.config import APIConfig, get_optimal_data_source


def _log_provider_usage_mock(provider: str, event_type: str, **kwargs) -> None:
    """Mock function for provider usage logging (GUI-specific)."""
    pass


from .meteostat_provider import MeteostatProvider  # noqa: E402
from .openmeteo_provider import OpenMeteoProvider  # noqa: E402
from .weather_provider_base import WeatherProvider  # noqa: E402
from .weather_types import ProviderNotAvailableError, WeatherAPIError  # noqa: E402

logger = logging.getLogger(__name__)


class WeatherClient:
    """
    Main weather client with multi-year support.

    Manages multiple weather providers with automatic fallback
    and retry logic. Supports queries for any time period with
    automatic batching.
    """

    def __init__(self, preferred_provider: str = "auto"):
        """Initialize weather client."""
        self.preferred_provider = preferred_provider
        self.current_provider: Optional[str] = None
        self.provider_usage_stats: Dict[str, int] = {}

        self.providers: Dict[str, WeatherProvider] = {
            "open-meteo": OpenMeteoProvider(),
            "meteostat": MeteostatProvider(),
        }

        self.max_retries = APIConfig.MAX_RETRIES
        self.retry_delay = 1.0

        self.provider_change_callback: Optional[Callable[[str, str], None]] = None
        self.provider_fallback_callback: Optional[Callable[[str, str], None]] = None

        logger.info(f"WeatherClient initialized (preferred: {preferred_provider})")

    def set_provider_change_callback(
        self, callback: Callable[[str, str], None]
    ) -> None:
        """Set callback for provider changes."""
        self.provider_change_callback = callback

    def set_provider_fallback_callback(
        self, callback: Callable[[str, str], None]
    ) -> None:
        """Set callback for provider fallback."""
        self.provider_fallback_callback = callback

    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        user_override_provider: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get weather data with automatic batching.

        Args:
            latitude, longitude: Geographic coordinates
            start_date, end_date: Date range (YYYY-MM-DD)
            user_override_provider: Force specific provider

        Returns:
            List of daily weather records with data_source in each record
        """
        logger.info(
            f"Weather request: {latitude:.4f}, {longitude:.4f} ({start_date} → {end_date})"
        )

        self._validate_inputs(latitude, longitude, start_date, end_date)

        selected_provider = self._select_provider(user_override_provider)
        if not selected_provider:
            raise ProviderNotAvailableError("No provider available")

        fallback_chain = self._get_provider_fallback_chain(selected_provider)

        last_error = None
        for attempt_provider in fallback_chain:
            try:
                logger.info(f"Trying provider: {attempt_provider}")

                provider = self.providers.get(attempt_provider)
                if not provider or not provider.validate_provider():
                    continue

                weather_data = self._retry_weather_request(
                    provider, latitude, longitude, start_date, end_date
                )

                self._handle_successful_request(attempt_provider, selected_provider)
                self.provider_usage_stats[attempt_provider] = (
                    self.provider_usage_stats.get(attempt_provider, 0) + 1
                )
                _log_provider_usage_mock(attempt_provider, "weather_data", success=True)

                return weather_data

            except (WeatherAPIError, Exception) as e:
                last_error = e
                logger.error(f"Provider {attempt_provider} failed: {e}")
                _log_provider_usage_mock(
                    attempt_provider, "weather_data", success=False
                )
                continue

        raise ProviderNotAvailableError(
            f"All providers failed. Last error: {last_error}"
        )

    def _is_valid_provider(self, provider_name: str) -> bool:
        """Return True when provider exists and validates."""
        return (
            provider_name in self.providers
            and self.providers[provider_name].validate_provider()
        )

    def _select_override_provider(self, user_override: Optional[str]) -> Optional[str]:
        """Return valid override provider when available."""
        if user_override and self._is_valid_provider(user_override):
            return user_override
        return None

    def _select_auto_provider(self) -> Optional[str]:
        """Select best available provider in auto mode."""
        optimal = get_optimal_data_source("single_city", prefer_free=True)
        if self._is_valid_provider(optimal):
            return optimal
        return self._select_first_valid_provider()

    def _select_first_valid_provider(self) -> Optional[str]:
        """Select the first valid provider from configured providers."""
        for provider_id, provider in self.providers.items():
            if provider.validate_provider():
                return provider_id
        return None

    def _select_preferred_provider(self) -> Optional[str]:
        """Select explicitly preferred provider or recurse to auto fallback."""
        if self.preferred_provider in self.providers:
            if self.providers[self.preferred_provider].validate_provider():
                return self.preferred_provider
            return self._select_provider(None)
        return None

    def _select_provider(self, user_override: Optional[str] = None) -> Optional[str]:
        """Select the best provider for the request."""
        override_provider = self._select_override_provider(user_override)
        if override_provider is not None:
            return override_provider

        if self.preferred_provider == "auto":
            return self._select_auto_provider()
        return self._select_preferred_provider()

    def _get_provider_fallback_chain(self, primary_provider: str) -> List[str]:
        """Get provider fallback chain."""
        available_providers = [
            provider_id
            for provider_id, provider in self.providers.items()
            if provider.validate_provider()
        ]

        if primary_provider in available_providers:
            available_providers.remove(primary_provider)
            available_providers.insert(0, primary_provider)

        return available_providers

    def _retry_weather_request(
        self,
        provider: WeatherProvider,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """Retry weather request with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                result = provider.get_weather_data(
                    latitude, longitude, start_date, end_date
                )
                return result

            except WeatherAPIError:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (attempt + 1)
                    time.sleep(delay)
                else:
                    raise

        return []

    def _handle_successful_request(
        self, used_provider: str, requested_provider: str
    ) -> None:
        """Handle successful request callbacks."""
        self.current_provider = used_provider

        if used_provider != requested_provider and self.provider_fallback_callback:
            self.provider_fallback_callback(requested_provider, used_provider)

        if (
            used_provider != self.preferred_provider
            and self.preferred_provider != "auto"
        ):
            if self.provider_change_callback:
                self.provider_change_callback(self.preferred_provider, used_provider)

    def _validate_inputs(
        self, latitude: float, longitude: float, start_date: str, end_date: str
    ) -> None:
        """Validate input parameters."""
        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid latitude: must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid longitude: must be between -180 and 180")

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format - use YYYY-MM-DD")

        if start_dt > end_dt:
            raise ValueError("Start date cannot be after end date")


__all__ = ["WeatherClient"]
