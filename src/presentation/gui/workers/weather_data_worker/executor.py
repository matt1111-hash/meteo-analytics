#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
WeatherDataWorker Executor - Main execution logic with cancellation support.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherDataWorker


def _is_cancelled(worker: "WeatherDataWorker", phase: str) -> bool:
    """Return cancellation status and emit a debug line when cancelled."""
    if worker.isInterruptionRequested() or worker.is_cancelled:
        print(f"🛑 DEBUG: Weather data fetch cancelled {phase}")
        return True
    return False


def _log_request_debug(
    worker: "WeatherDataWorker", selected_provider: str, api_url: str
) -> None:
    """Log request debug information."""
    from ...utils import get_source_display_name

    print(f"🌍 DEBUG: Provider routing - {get_source_display_name(selected_provider)}")
    print(f"🌪️ DEBUG: Wind gusts kérés: {worker.latitude:.4f}, {worker.longitude:.4f}")
    print(f"📅 DEBUG: Időszak: {worker.start_date} - {worker.end_date}")
    print(f"🔗 DEBUG: API URL: {api_url}")


def _select_provider(worker_executor: "WorkerExecutor") -> str | None:
    """Select a provider unless cancellation was requested."""
    worker_executor._worker.emit_status("🌍 Provider kiválasztása...")
    worker_executor._worker.progress_updated.emit(5)
    if _is_cancelled(worker_executor._worker, "at start"):
        return None
    selected_provider = worker_executor._select_optimal_provider()
    if selected_provider:
        worker_executor._worker.progress_updated.emit(10)
    return selected_provider


def _prepare_request(worker_executor: "WorkerExecutor", selected_provider: str):
    """Prepare request metadata unless cancelled."""
    if _is_cancelled(worker_executor._worker, "after provider selection"):
        return None
    api_url, api_params = worker_executor._worker._build_api_request(selected_provider)
    worker_executor._worker.progress_updated.emit(20)
    _log_request_debug(worker_executor._worker, selected_provider, api_url)
    if _is_cancelled(worker_executor._worker, "before HTTP requests"):
        return None
    return api_url, api_params


def _finalize_weather_response(worker_executor: "WorkerExecutor") -> None:
    """Finalize the worker response and emit success or validation error."""
    if worker_executor._worker.weather_data:
        worker_executor._worker.emit_status("🌪️ Széllökés adatok validálása...")
        worker_executor._worker._validate_wind_gusts_data()
        worker_executor._worker.progress_updated.emit(100)
        if not worker_executor._worker.is_cancelled:
            worker_executor._worker.weather_data_completed.emit(
                worker_executor._worker.weather_data
            )
            worker_executor._worker.emit_status(
                "✅ Időjárási adatok sikeresen lekérdezve"
            )
            print("✅ DEBUG: Weather data completed and emitted")
        return
    worker_executor._worker.emit_error("Érvénytelen API válasz struktúra")


class WorkerExecutor:
    """Execute weather data fetch with cancellation support."""

    def __init__(self, worker: "WeatherDataWorker"):
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
            selected_provider = _select_provider(self)
            if selected_provider is None:
                self._worker.emit_error("Egyik provider sem elérhető")
                return
            request_data = _prepare_request(self, selected_provider)
            if request_data is None:
                return
            api_url, api_params = request_data
            success = self._execute_with_fallback(
                selected_provider, api_url, api_params
            )

            if not success:
                self._worker.emit_error("Minden provider API hívás sikertelen")
                return

            self._worker.progress_updated.emit(90)
            if _is_cancelled(self._worker, "before completion"):
                return
            _finalize_weather_response(self)

        except Exception as e:
            if not self._worker.is_cancelled:
                self._worker.emit_error(f"Váratlan hiba: {str(e)}")

    def _select_optimal_provider(self):
        """Select optimal provider."""
        return self._provider_selector.select_optimal()

    def _execute_with_fallback(
        self, selected_provider: str, api_url: str, params
    ) -> bool:
        """Execute HTTP requests with provider fallback."""
        from ...utils import (
            get_fallback_source_chain,
            get_source_display_name,
            log_provider_usage_event,
        )

        success = False
        fallback_chain = get_fallback_source_chain(selected_provider)

        for provider_index, provider in enumerate(fallback_chain):
            if _is_cancelled(self._worker, "in fallback loop"):
                return False

            try:
                self._worker.emit_status(
                    f"📡 {get_source_display_name(provider)} API kérés..."
                )
                self._worker.progress_updated.emit(30 + (provider_index * 20))

                api_url, api_params = self._worker._build_api_request(provider)
                success = self._worker._execute_api_request(
                    provider, api_url, api_params
                )

                if success:
                    if provider != selected_provider:
                        print(
                            f"🔄 DEBUG: Provider fallback: {selected_provider} → {provider}"
                        )
                        self._worker.provider_fallback_occurred.emit(
                            selected_provider, provider
                        )

                    self._worker.actual_provider = provider
                    log_provider_usage_event(provider, "weather_data", True)
                    self._worker.emit_status(
                        f"✅ {get_source_display_name(provider)} sikeres"
                    )
                    break

            except Exception as e:
                print(f"❌ DEBUG: Provider {provider} failed: {e}")
                log_provider_usage_event(provider, "weather_data", False)

                if provider_index < len(fallback_chain) - 1:
                    self._worker.emit_status(
                        f"⚠️ {get_source_display_name(provider)} sikertelen, fallback..."
                    )

        return success


# Import here to avoid circular dependency
from .provider_selector import ProviderSelector  # noqa: E402
