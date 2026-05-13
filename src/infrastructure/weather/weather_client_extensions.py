#!/usr/bin/env python3
"""
Weather Client - Provider Management and Extensions
Global Weather Analyzer project

Part of the weather_client refactoring - split into focused modules.
"""

import logging
from typing import Any

from src.config import get_source_display_name

from .weather_client_core import WeatherClient

logger = logging.getLogger(__name__)


class WeatherClientExtensions(WeatherClient):
    """
    WeatherClient with provider management and backward compatibility methods.

    Extends the core WeatherClient with additional functionality
    for provider management and legacy API compatibility.
    """

    def set_preferred_provider(self, provider: str) -> None:
        """Set preferred provider."""
        if provider == "auto" or provider in self.providers:
            self.preferred_provider = provider
            logger.info(f"Preferred provider changed: {get_source_display_name(provider)}")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_current_provider(self) -> str | None:
        """Get current provider."""
        return self.current_provider

    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        return [
            provider_id
            for provider_id, provider in self.providers.items()
            if provider.validate_provider()
        ]

    def get_provider_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all providers."""
        status = {}

        for provider_id, provider in self.providers.items():
            available = provider.validate_provider()
            status[provider_id] = {
                "display_name": provider.display_name,
                "available": available,
                "request_count": provider.get_request_count(),
                "usage_count": self.provider_usage_stats.get(provider_id, 0),
                "is_current": self.current_provider == provider_id,
            }

        return status

    def reset_provider_usage_stats(self) -> None:
        """Reset provider usage statistics."""
        self.provider_usage_stats.clear()
        for provider in self.providers.values():
            provider.reset_request_count()
        logger.info("Provider usage stats reset")

    # Backward compatibility methods
    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        user_override_provider: str | None = None,
    ) -> tuple[dict[str, Any] | None, str]:
        """Get current weather (backward compatibility)."""
        from datetime import datetime  # noqa: PLC0415

        today = datetime.now().strftime("%Y-%m-%d")

        try:
            weather_data = self.get_weather_data(
                latitude, longitude, today, today, user_override_provider
            )

            if weather_data:
                source = weather_data[0].get("data_source", "unknown")
                return (weather_data[0], source)
            return (None, "no_data")

        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return (None, "error")

    def get_weather_for_date_range(
        self,
        latitude: float,
        longitude: float,
        days_back: int = 7,
        user_override_provider: str | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        """Get weather for date range (backward compatibility)."""
        from datetime import datetime, timedelta  # noqa: PLC0415

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        weather_data = self.get_weather_data(
            latitude,
            longitude,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            user_override_provider,
        )

        source = weather_data[0].get("data_source", "unknown") if weather_data else "no_data"
        return (weather_data, source)


__all__ = ["WeatherClientExtensions"]
