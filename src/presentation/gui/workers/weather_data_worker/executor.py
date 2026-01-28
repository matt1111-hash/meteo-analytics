#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherDataWorker Executor - Main execution logic with cancellation support.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherDataWorker


class WorkerExecutor:
    """Execute weather data fetch with cancellation support."""

    def __init__(self, worker: 'WeatherDataWorker'):
        """
        Initialize worker executor.

        Args:
            worker: WeatherDataWorker instance
        """
        self._worker = worker
        self._provider_selector = ProviderSelector(worker)

    def execute(self) -> None:
        """Execute weather data fetch with cancellation checks."""
        try:
            self._worker.emit_status("🌍 Provider kiválasztása...")
            self._worker.progress_updated.emit(5)

            # Cancellation check at start
            if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled at start")
                return

            # Provider selection
            selected_provider = self._select_optimal_provider()
            if not selected_provider:
                self._worker.emit_error("Egyik provider sem elérhető")
                return

            self._worker.progress_updated.emit(10)

            # Cancellation check after provider selection
            if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled after provider selection")
                return

            # Build API request
            from ...utils import get_source_display_name
            api_url, api_params = self._worker._build_api_request(selected_provider)

            self._worker.progress_updated.emit(20)

            print(f"🌍 DEBUG: Provider routing - {get_source_display_name(selected_provider)}")
            print(f"🌪️ DEBUG: Wind gusts kérés: {self._worker.latitude:.4f}, {self._worker.longitude:.4f}")
            print(f"📅 DEBUG: Időszak: {self._worker.start_date} - {self._worker.end_date}")
            print(f"🔗 DEBUG: API URL: {api_url}")

            # Cancellation check before HTTP requests
            if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled before HTTP requests")
                return

            # HTTP request with provider fallback
            success = self._execute_with_fallback(selected_provider, api_url, api_params)

            if not success:
                self._worker.emit_error("Minden provider API hívás sikertelen")
                return

            self._worker.progress_updated.emit(90)

            # Final cancellation check
            if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled before completion")
                return

            # Wind gusts validation and response processing
            if self._worker.weather_data:
                self._worker.emit_status("🌪️ Széllökés adatok validálása...")
                self._worker._validate_wind_gusts_data()
                self._worker.progress_updated.emit(100)

                if not self._worker.is_cancelled:
                    self._worker.weather_data_completed.emit(self._worker.weather_data)
                    self._worker.emit_status("✅ Időjárási adatok sikeresen lekérdezve")
                    print("✅ DEBUG: Weather data completed and emitted")
            else:
                self._worker.emit_error("Érvénytelen API válasz struktúra")

        except Exception as e:
            if not self._worker.is_cancelled:
                self._worker.emit_error(f"Váratlan hiba: {str(e)}")

    def _select_optimal_provider(self):
        """Select optimal provider."""
        return self._provider_selector.select_optimal()

    def _execute_with_fallback(self, selected_provider: str, api_url: str, params) -> bool:
        """Execute HTTP requests with provider fallback."""
        from ...utils import get_fallback_source_chain, get_source_display_name, log_provider_usage_event

        success = False
        fallback_chain = get_fallback_source_chain(selected_provider)

        for provider_index, provider in enumerate(fallback_chain):
            # Cancellation check in fallback loop
            if self._worker.isInterruptionRequested() or self._worker.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled in fallback loop")
                return False

            try:
                self._worker.emit_status(f"📡 {get_source_display_name(provider)} API kérés...")
                self._worker.progress_updated.emit(30 + (provider_index * 20))

                api_url, api_params = self._worker._build_api_request(provider)
                success = self._worker._execute_api_request(provider, api_url, api_params)

                if success:
                    if provider != selected_provider:
                        print(f"🔄 DEBUG: Provider fallback: {selected_provider} → {provider}")
                        self._worker.provider_fallback_occurred.emit(selected_provider, provider)

                    self._worker.actual_provider = provider
                    log_provider_usage_event(provider, "weather_data", True)
                    self._worker.emit_status(f"✅ {get_source_display_name(provider)} sikeres")
                    break

            except Exception as e:
                print(f"❌ DEBUG: Provider {provider} failed: {e}")
                log_provider_usage_event(provider, "weather_data", False)

                if provider_index < len(fallback_chain) - 1:
                    self._worker.emit_status(f"⚠️ {get_source_display_name(provider)} sikertelen, fallback...")
                    continue

        return success


# Import here to avoid circular dependency
from .provider_selector import ProviderSelector
