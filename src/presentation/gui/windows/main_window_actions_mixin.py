# mypy: ignore-errors
"""Action wrappers and cleanup helpers for the main window."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..analytics import AnalyticsView
from .main_window_actions import (
    handle_analytics_view_query,
    handle_export_request,
    handle_multi_city_weather_request,
    map_query_type_to_parameter,
    register_thread,
    register_timer,
    register_web_view,
    register_worker,
    show_about,
    show_error,
    show_extreme_weather,
    switch_view,
)

if TYPE_CHECKING:
    from src.domain.entities.analytics_models import AnalyticsResult

    from .main_window import MainWindow


class MainWindowActionsMixin:
    """Thin wrappers around extracted window actions."""

    def _handle_export_request(self: MainWindow, format: str) -> None:
        """Delegate export handling."""
        handle_export_request(self, format)

    def _show_extreme_weather(self: MainWindow) -> None:
        """Open the extreme weather dialog."""
        show_extreme_weather(self)

    def _handle_analytics_view_query(self: MainWindow, query_type: str, region_name: str) -> None:
        """Delegate analytics queries."""
        handle_analytics_view_query(self, query_type, region_name)

    def _handle_multi_city_weather_request(
        self: MainWindow,
        analysis_type: str,
        region_id: str,
        start_date: str,
        end_date: str,
        params: dict,
    ) -> None:
        """Delegate multi-city weather requests."""
        handle_multi_city_weather_request(
            self,
            analysis_type,
            region_id,
            start_date,
            end_date,
            params,
        )

    def _map_query_type_to_parameter(self: MainWindow, query_type: str) -> str:
        """Delegate query type mapping."""
        return map_query_type_to_parameter(query_type)

    def _on_multi_city_result_ready_for_views(
        self: MainWindow,
        result: AnalyticsResult,
        query_type: str = "hottest_today",
    ) -> None:
        """Forward multi-city result routing."""
        from .main_window_actions import on_multi_city_result_ready  # noqa: PLC0415

        on_multi_city_result_ready(self, result, query_type)

    def _show_about(self: MainWindow) -> None:
        """Open the about dialog."""
        show_about(self)

    def _show_error(self: MainWindow, message: str) -> None:
        """Show an error dialog."""
        show_error(self, message)

    def _register_thread(self: MainWindow, thread: QThread) -> None:
        """Track a thread for cleanup."""
        register_thread(self, thread)

    def _register_worker(self: MainWindow, worker: object) -> None:
        """Track a worker for cleanup."""
        register_worker(self, worker)

    def _register_web_view(self: MainWindow, web_view: QWebEngineView) -> None:
        """Track a web view for cleanup."""
        register_web_view(self, web_view)

    def _register_timer(self: MainWindow, timer: QTimer) -> None:
        """Track a timer for cleanup."""
        register_timer(self, timer)

    def get_current_view(self: MainWindow) -> str:
        """Return the current view name."""
        return self.state.current_view_name

    def switch_to_view(self: MainWindow, view_name: str) -> None:
        """Switch views through the public API."""
        switch_view(self, view_name)

    def get_analytics_panel(self: MainWindow) -> AnalyticsView | None:
        """Return the analytics panel."""
        return self.analytics_panel

    def focus_analytics_panel(self: MainWindow) -> None:
        """Switch to the analytics panel when available."""
        if self.analytics_panel:
            switch_view(self, "analytics")
