# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for api_settings_widget.py."""

from __future__ import annotations

from .api_settings_widget_part1 import ApiSettingsWidgetPart1Mixin
from .api_settings_widget_part2 import ApiSettingsWidgetPart2Mixin
from .api_settings_widget_support import *


class ApiSettingsWidget(ApiSettingsWidgetPart1Mixin, ApiSettingsWidgetPart2Mixin, QWidget):
    """
    ⚙️ API BEÁLLÍTÁSOK WIDGET - CLEAN ARCHITECTURE

    Felelősség:
    - API timeout beállítás (multi-year batch optimalizált)
    - Automatikus timezone detection
    - Data caching enable/disable
    - Settings validation és persistence

    Interface:
    - api_settings_changed = Signal(dict) - settings változás
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - valid beállítások
    """

    # === KIMENŐ SIGNALOK ===
    api_settings_changed = Signal(dict)  # settings dict
