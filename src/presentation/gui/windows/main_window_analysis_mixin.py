# mypy: ignore-errors
"""Analysis and provider signal handling for the main window."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .main_window import MainWindow


def _connect_signals_if_present(source: Any, signal_map: list[tuple[str, Any]]) -> None:
    """Connect named Qt signals when present on the source object."""
    for signal_name, handler in signal_map:
        if hasattr(source, signal_name):
            getattr(source, signal_name).connect(handler)


class MainWindowAnalysisMixin:
    """Signal wiring and analysis lifecycle handlers."""

    def _connect_mvc_signals(self: "MainWindow") -> None:
        """Connect controller and widget signals."""
        _connect_signals_if_present(
            self.controller,
            [
                ("analysis_started", self._on_analysis_started),
                ("analysis_completed", self._on_analysis_completed),
                ("analysis_failed", self._on_analysis_failed),
                ("analysis_cancelled", self._on_analysis_cancelled),
            ],
        )
        _connect_signals_if_present(
            self.control_panel,
            [
                ("provider_selected", self._on_provider_selected),
                ("provider_usage_updated", self._on_provider_usage_updated),
                ("provider_warning", self._on_provider_warning),
                ("provider_fallback", self._on_provider_fallback),
                ("local_error_occurred", self._on_local_error),
                ("analysis_requested", self._on_analysis_requested),
            ],
        )
        _connect_signals_if_present(
            self.results_panel,
            [
                ("export_requested", self._handle_export_request),
                ("extreme_weather_requested", self._show_extreme_weather),
            ],
        )
        _connect_signals_if_present(
            self.analytics_panel,
            [("query_requested", self._handle_analytics_view_query)],
        )

    def _on_local_error(self: "MainWindow", error_message: str) -> None:
        """Display local UI errors."""
        self.status_bar.showMessage(f"❌ {error_message}", 5000)
        self._show_error(error_message)

    def _on_analysis_requested(self: "MainWindow", request: dict[str, Any]) -> None:
        """Forward analysis requests to the controller."""
        print("=" * 80)
        print("🚨 DEBUG: MainWindow._on_analysis_requested() MEGHÍVVA!")
        print(f"🚨 DEBUG: Request data: {request}")
        print(f"🚨 DEBUG: Analysis type: {request.get('analysis_type', 'unknown')}")
        print("=" * 80)
        try:
            print("🚨 DEBUG: Calling controller.handle_analysis_request()...")
            self.controller.handle_analysis_request(request)
            print("🚨 DEBUG: controller.handle_analysis_request() returned")
        except Exception as exc:
            print(f"❌ DEBUG: Exception in controller.handle_analysis_request(): {exc}")
            import traceback

            traceback.print_exc()
            self.status_bar.showMessage(f"❌ Hiba: {exc}")
            self._show_error(f"Elemzési hiba: {exc}")

    def _on_provider_selected(self: "MainWindow", provider_name: str) -> None:
        """Handle provider selection changes."""
        self.state.provider.current_provider = provider_name
        self._update_provider_status_display()

    def _on_provider_usage_updated(
        self: "MainWindow", usage_stats: dict[str, dict[str, Any]]
    ) -> None:
        """Refresh provider usage state."""
        self.state.provider.provider_usage_stats = usage_stats
        self.state.update_provider_warning()
        self._update_provider_status_display()

    def _on_provider_warning(
        self: "MainWindow", provider_name: str, usage_percent: int
    ) -> None:
        """Refresh the provider status when warnings change."""
        self._update_provider_status_display()

    def _on_provider_fallback(
        self: "MainWindow", from_provider: str, to_provider: str
    ) -> None:
        """Display provider fallback information."""
        self.status_bar.showMessage(
            f"⚠️ Provider fallback: {from_provider} → {to_provider}"
        )

    def _on_analysis_started(self: "MainWindow", analysis_type: str) -> None:
        """Show analysis start feedback."""
        self.status_bar.showMessage(f"🔄 {analysis_type} elemzés indítása...")

    def _on_analysis_completed(self: "MainWindow", result_data: dict[str, Any]) -> None:
        """Push completed analysis results into the results panel."""
        print("=" * 80)
        print("🚨 DEBUG: MainWindow._on_analysis_completed() ELEJE")
        print(f"🚨 DEBUG: result_data keys: {list(result_data.keys())}")

        request_params = result_data.get("request_params", {})
        print(f"🚨 DEBUG: request_params keys: {list(request_params.keys())}")

        location_data = request_params.get("location_data", {})
        print(f"🚨 DEBUG: location_data keys: {list(location_data.keys())}")
        print(f"🚨 DEBUG: location_data: {location_data}")

        city_name = (
            location_data.get("name")
            or location_data.get("city_name")
            or location_data.get("display_name")
            or "Ismeretlen"
        )
        print(f"🚨 DEBUG: city_name extracted: '{city_name}'")
        print("=" * 80)

        self.status_bar.showMessage("✅ Elemzés befejezve")
        weather_data = result_data.get("result_data", {})
        if hasattr(self.results_panel, "update_data"):
            self.results_panel.update_data(weather_data, city_name)
        else:
            print("⚠️ WARNING: results_panel has no update_data method")

    def _on_analysis_failed(self: "MainWindow", error_message: str) -> None:
        """Handle failed analyses."""
        self.status_bar.showMessage(f"❌ Elemzés hiba: {error_message}")
        self._show_error(error_message)

    def _on_analysis_cancelled(self: "MainWindow") -> None:
        """Handle cancelled analyses."""
        self.status_bar.showMessage("⚠️ Elemzés megszakítva")
