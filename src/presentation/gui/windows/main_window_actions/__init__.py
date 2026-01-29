"""Main Window Actions - re-export for backward compatibility."""
from src.presentation.gui.windows.main_window_actions.navigation import (
    switch_view,
    handle_analytics_view_query,
    handle_multi_city_weather_request,
    on_multi_city_result_ready,
    map_query_type_to_parameter,
)
from src.presentation.gui.windows.main_window_actions.dialogs import (
    handle_export_request,
    show_extreme_weather,
    show_about,
    show_error,
    register_thread,
    register_worker,
    register_web_view,
    register_timer,
    cleanup_all_threads,
    cleanup_all_workers,
    cleanup_all_web_engines,
    cleanup_all_timers,
)

__all__ = [
    'switch_view',
    'handle_analytics_view_query',
    'handle_multi_city_weather_request',
    'on_multi_city_result_ready',
    'map_query_type_to_parameter',
    'handle_export_request',
    'show_extreme_weather',
    'show_about',
    'show_error',
    'register_thread',
    'register_worker',
    'register_web_view',
    'register_timer',
    'cleanup_all_threads',
    'cleanup_all_workers',
    'cleanup_all_web_engines',
    'cleanup_all_timers',
]
