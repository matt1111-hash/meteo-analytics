#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherDataWorker API Executor - Execute HTTP API requests.
"""

import json
from typing import TYPE_CHECKING, Any, Dict

import httpx

if TYPE_CHECKING:
    from .core import WeatherDataWorker


class APIExecutor:
    """Execute HTTP API requests."""

    def __init__(self, worker: "WeatherDataWorker"):
        """
        Initialize API executor.

        Args:
            worker: WeatherDataWorker instance
        """
        self._worker = worker

    def execute_request(
        self, provider: str, api_url: str, params: Dict[str, Any]
    ) -> bool:
        """
        Execute API request with cancellation support.

        Args:
            provider: Provider identifier
            api_url: API endpoint URL
            params: Request parameters

        Returns:
            True if successful
        """
        try:
            from ...utils import APIConstants, get_source_display_name

            headers = self.get_provider_headers(provider)
            timeout = APIConstants.DEFAULT_TIMEOUT

            with httpx.Client(timeout=timeout, headers=headers) as client:
                # Cancellation check before HTTP call
                if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                    print(f"🛑 DEBUG: {provider} API request cancelled before send")
                    return False

                self._worker.emit_status(
                    f"📡 {get_source_display_name(provider)} HTTP kérés..."
                )
                response = client.get(api_url, params=params)

                # Cancellation check after HTTP call
                if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                    print(f"🛑 DEBUG: {provider} API response cancelled after receive")
                    return False

                if response.status_code != 200:
                    print(f"❌ DEBUG: {provider} API hiba: HTTP {response.status_code}")
                    return False

                self._worker.emit_status(
                    f"📄 {get_source_display_name(provider)} válasz feldolgozása..."
                )
                self._worker.weather_data = response.json()

                # Provider change notification
                if (
                    provider != self._worker.preferred_provider
                    and self._worker.preferred_provider != "auto"
                ):
                    if not self._worker.is_cancelled:
                        self._worker.provider_changed.emit(provider)

                return True

        except httpx.TimeoutException:
            print(f"⏱️ DEBUG: {provider} API timeout")
            return False
        except httpx.RequestError as e:
            print(f"🌐 DEBUG: {provider} network error: {e}")
            return False
        except json.JSONDecodeError:
            print(f"📄 DEBUG: {provider} JSON decode error")
            return False
        except Exception as e:
            print(f"❌ DEBUG: {provider} unexpected error: {e}")
            return False

    def get_provider_headers(self, provider: str) -> Dict[str, str]:
        """
        Get provider-specific HTTP headers.

        Args:
            provider: Provider identifier

        Returns:
            HTTP headers dictionary
        """
        from ...utils import APIConstants

        base_headers = {"User-Agent": APIConstants.USER_AGENT}

        if provider == "meteostat":
            import os

            api_key = os.getenv("METEOSTAT_API_KEY")
            if api_key:
                base_headers["X-RapidAPI-Key"] = api_key
                base_headers["X-RapidAPI-Host"] = "meteostat.p.rapidapi.com"

        return base_headers
