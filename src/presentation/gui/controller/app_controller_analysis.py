# mypy: ignore-errors
"""Analysis and request handling for the GUI app controller."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot

from ..workers.analysis_worker import AnalysisWorker

if TYPE_CHECKING:
    from .app_controller import AppController


class AppControllerAnalysisMixin:
    """Methods related to analysis and request forwarding."""

    @Slot(dict)
    def handle_analysis_request(
        self: "AppController", request_data: dict[str, Any]
    ) -> None:
        """Handle a full analysis request payload."""
        print("=" * 80)
        print("🚨 DEBUG: AppController.handle_analysis_request() MEGHÍVVA!")
        print(f"🚨 DEBUG: Request data: {request_data}")
        print(
            f"🚨 DEBUG: Analysis type: {request_data.get('analysis_type', 'unknown')}"
        )
        print("=" * 80)

        def start_analysis_callback(
            enhanced_request: dict[str, Any], handler: Any
        ) -> Any:
            """Start the analysis worker through the handler."""
            print("=" * 80)
            print("🚨 DEBUG: start_analysis_callback() MEGHÍVVA!")
            print(f"🚨 DEBUG: enhanced_request={enhanced_request}")
            print("=" * 80)

            worker = AnalysisWorker(parent=self)
            handler.set_active_worker(worker)

            worker.progress_updated.connect(handler.on_analysis_progress)
            worker.analysis_completed.connect(handler.on_analysis_completed)
            worker.analysis_failed.connect(handler.on_analysis_failed)
            worker.analysis_cancelled.connect(handler.on_analysis_cancelled)

            print("🚨 DEBUG: worker.start_analysis() HÍVÁS ELŐTT")
            result = worker.start_analysis(enhanced_request)
            print(f"🚨 DEBUG: worker.start_analysis() VISSZATÉRT: result={result}")
            return result

        print("🚨 DEBUG: analysis_handler.handle_analysis_request() HÍVÁS ELŐTT")
        self.analysis_handler.handle_analysis_request(
            request_data,
            self.provider_routing,
            start_analysis_callback,
        )
        print("🚨 DEBUG: analysis_handler.handle_analysis_request() VISSZATÉRT")

    @Slot(dict)
    def _on_analysis_completed_forward(
        self: "AppController", result_data: dict[str, Any]
    ) -> None:
        """Forward the completed analysis to downstream signals."""
        print("=" * 80)
        print("🚨 DEBUG: AppController._on_analysis_completed_forward() ELEJE")
        print(f"🚨 DEBUG: result_data keys: {list(result_data.keys())}")
        print("=" * 80)

        analysis_type = self.analysis_handler.analysis_state.get(
            "analysis_type",
            "unknown",
        )
        self.analysis_completed.emit(result_data)

        if analysis_type == "single_location":
            self.weather_data_ready.emit(result_data)

    def stop_current_analysis(self: "AppController") -> None:
        """Stop the currently running analysis."""
        self.analysis_handler.stop_current_analysis()

    def is_analysis_running(self: "AppController") -> bool:
        """Return whether an analysis is currently running."""
        return self.analysis_handler.is_analysis_running()

    def get_current_analysis_info(self: "AppController") -> dict[str, Any]:
        """Return details about the current analysis."""
        return self.analysis_handler.get_current_analysis_info()

    @Slot(float, float, str, str, dict)
    def handle_weather_data_request(
        self: "AppController",
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        params: dict[str, Any],
    ) -> None:
        """Translate legacy weather requests to the analysis pipeline."""
        self._logger.warning("🌐🌪️ DEPRECATED: handle_weather_data_request használata.")
        analysis_request = {
            "analysis_type": "single_location",
            "location_data": {
                "lat": latitude,
                "lon": longitude,
                "name": self.current_city_data.get("name", "Unknown")
                if self.current_city_data
                else "Unknown",
            },
            "date_range": {"start_date": start_date, "end_date": end_date},
            "api_params": params,
        }
        self.handle_analysis_request(analysis_request)
