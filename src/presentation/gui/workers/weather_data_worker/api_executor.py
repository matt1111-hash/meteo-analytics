#!/usr/bin/env python3
# mypy: ignore-errors

"""
WeatherDataWorker API Executor - Execute HTTP API requests.
"""

import json
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from .core import WeatherDataWorker


def _is_cancelled(worker: "WeatherDataWorker", provider: str, phase: str) -> bool:
    """Return cancellation status and emit a debug line when cancelled."""
    if worker.isInterruptionRequested() or worker.is_cancelled:
        print(f"🛑 DEBUG: {provider} API request cancelled {phase}")
        return True
    return False


def _notify_provider_change(worker: "WeatherDataWorker", provider: str) -> None:
    """Emit provider change notification when needed."""
    if worker.preferred_provider not in (provider, "auto") and not worker.is_cancelled:
        worker.provider_changed.emit(provider)


class APIExecutor:
    """Execute HTTP API requests."""

    def __init__(self, worker: "WeatherDataWorker"):
        """
        Initialize API executor.

        Args:
            worker: WeatherDataWorker instance
        """
        self._worker = worker

    def execute_request(  # noqa: PLR0911
        self, provider: str, api_url: str, params: dict[str, Any]
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
            from ...utils import APIConstants, get_source_display_name  # noqa: PLC0415

            headers = self.get_provider_headers(provider)
            timeout = APIConstants.DEFAULT_TIMEOUT

            with httpx.Client(timeout=timeout, headers=headers) as client:
                if _is_cancelled(self._worker, provider, "before send"):
                    return False

                self._worker.emit_status(f"📡 {get_source_display_name(provider)} HTTP kérés...")
                response = client.get(api_url, params=params)

                if _is_cancelled(self._worker, provider, "after receive"):
                    return False

                if response.status_code != 200:  # noqa: PLR2004
                    print(f"❌ DEBUG: {provider} API hiba: HTTP {response.status_code}")
                    return False

                self._worker.emit_status(
                    f"📄 {get_source_display_name(provider)} válasz feldolgozása..."
                )
                self._worker.weather_data = response.json()
                _notify_provider_change(self._worker, provider)
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

    def get_provider_headers(self, provider: str) -> dict[str, str]:
        """
        Get provider-specific HTTP headers.

        Args:
            provider: Provider identifier

        Returns:
            HTTP headers dictionary
        """
        from ...utils import APIConstants  # noqa: PLC0415

        base_headers = {"User-Agent": APIConstants.USER_AGENT}

        if provider == "meteostat":
            import os  # noqa: PLC0415

            api_key = os.getenv("METEOSTAT_API_KEY")
            if api_key:
                base_headers["X-RapidAPI-Key"] = api_key
                base_headers["X-RapidAPI-Host"] = "meteostat.p.rapidapi.com"

        return base_headers
