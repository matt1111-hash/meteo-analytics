# mypy: ignore-errors
"""Main Window Actions - re-export for backward compatibility."""

from src.presentation.gui.windows.main_window_actions import (
    cleanup_all_threads,
    cleanup_all_timers,
    cleanup_all_web_engines,
    cleanup_all_workers,
    handle_analytics_view_query,
    handle_export_request,
    handle_multi_city_weather_request,
    map_query_type_to_parameter,
    on_multi_city_result_ready,
    register_thread,
    register_timer,
    register_web_view,
    register_worker,
    show_about,
    show_error,
    show_extreme_weather,
    switch_view,
)

__all__ = [
    "switch_view",
    "handle_analytics_view_query",
    "handle_multi_city_weather_request",
    "on_multi_city_result_ready",
    "map_query_type_to_parameter",
    "handle_export_request",
    "show_extreme_weather",
    "show_about",
    "show_error",
    "register_thread",
    "register_worker",
    "register_web_view",
    "register_timer",
    "cleanup_all_threads",
    "cleanup_all_workers",
    "cleanup_all_web_engines",
    "cleanup_all_timers",
]
