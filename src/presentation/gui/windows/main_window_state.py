#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window State - Állapotkezelés a MainWindow számára.

FÁJL: src/presentation/gui/windows/main_window_state.py
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    from ..utils import ThemeType, get_provider_warning_level
except ImportError:

    class ThemeType:
        LIGHT = "light"
        DARK = "dark"

    def get_provider_warning_level(x):
        return "normal"


@dataclass
class ProviderState:
    """
    🌍 Provider állapot követés.
    """

    current_provider: str = "auto"
    provider_usage_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    provider_cost_summary: str = ""
    provider_warning_level: Optional[str] = None


@dataclass
class HungarianCountiesState:
    """
    🗺️ Magyar megyék állapot követés.
    """

    loaded: bool = False
    geodataframe: Optional[Any] = None


@dataclass
class MainWindowState:
    """
    🪟 Főablak állapotkezelés.
    """

    # Téma állapot
    current_theme: str = ThemeType.LIGHT
    current_view_name: str = "single_city"

    # Provider állapot
    provider: ProviderState = field(default_factory=ProviderState)

    # Magyar megyék állapot
    hungarian_counties: HungarianCountiesState = field(
        default_factory=HungarianCountiesState
    )

    # Cleanup tracking
    active_threads: list = field(default_factory=list)
    active_workers: list = field(default_factory=list)
    web_engine_views: list = field(default_factory=list)
    cleanup_timers: list = field(default_factory=list)

    def update_provider_warning(self) -> None:
        """
        🌍 Provider warning szint frissítése.
        """
        if self.provider.provider_usage_stats:
            usage = self.provider.provider_usage_stats.get(
                self.provider.current_provider, {}
            )
            daily_requests = usage.get("daily_requests", 0)
            self.provider.provider_warning_level = get_provider_warning_level(
                daily_requests
            )
        else:
            self.provider.provider_warning_level = "normal"

    def register_thread(self, thread) -> None:
        """Thread regisztrálása cleanup-hoz."""
        self.active_threads.append(thread)

    def register_worker(self, worker) -> None:
        """Worker regisztrálása cleanup-hoz."""
        self.active_workers.append(worker)

    def register_web_view(self, web_view) -> None:
        """WebEngine view regisztrálása cleanup-hoz."""
        self.web_engine_views.append(web_view)

    def register_timer(self, timer) -> None:
        """QTimer regisztrálása cleanup-hoz."""
        self.cleanup_timers.append(timer)


# Export
__all__ = [
    "ProviderState",
    "HungarianCountiesState",
    "MainWindowState",
]
