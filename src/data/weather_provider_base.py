#!/usr/bin/env python3
"""
Weather Provider - Abstract Base Class
Global Weather Analyzer project

Part of the weather_client refactoring - split into focused modules.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


class WeatherProvider(ABC):
    """
    Abstract base class for all weather providers.

    Defines the interface that all weather providers must implement.
    """

    def __init__(self, provider_id: str, display_name: str):
        """Initialize weather provider."""
        self.provider_id = provider_id
        self.display_name = display_name
        self.session = requests.Session()
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 0.1

        logger.info(f"Weather provider initialized: {display_name}")

    @abstractmethod
    def get_weather_data(
        self, latitude: float, longitude: float, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get weather data for the specified location and date range.

        Args:
            latitude, longitude: Geographic coordinates
            start_date, end_date: Date range (YYYY-MM-DD)

        Returns:
            List of daily weather records
        """
        pass

    @abstractmethod
    def validate_provider(self) -> bool:
        """
        Validate if provider is available and properly configured.

        Returns:
            True if provider is available
        """
        pass

    def _rate_limit_check(self) -> None:
        """Rate limiting check and delay."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

    def _update_request_tracking(self) -> None:
        """Update request tracking."""
        self.request_count += 1
        self.last_request_time = time.time()

    def get_request_count(self) -> int:
        """Get total request count."""
        return self.request_count

    def reset_request_count(self) -> None:
        """Reset request count."""
        self.request_count = 0


__all__ = ["WeatherProvider"]
