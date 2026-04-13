# ruff: noqa: F401, F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for public_api.py."""

from __future__ import annotations

from .public_api_part1 import (
    _update_title,
    _update_windy_days_tab,
    force_hide_loading,
    get_current_tab,
    get_loading_status,
    get_windy_days_tab,
    hide_loading_indicator,
    is_loading,
    show_loading_indicator,
    switch_to_tab,
    switch_to_windy_days_tab,
    trigger_windy_days_analysis,
    update_data,
    update_loading_progress,
)
from .public_api_part2 import (
    apply_theme,
    apply_theme_by_name,
    clear_data,
    get_charts_container,
    get_current_theme_name,
    get_data_table,
    trigger_extreme_weather_analysis,
)
from .public_api_support import *
