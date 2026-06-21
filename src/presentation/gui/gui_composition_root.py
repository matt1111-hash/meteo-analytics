#!/usr/bin/env python3
# ruff: noqa: PLC0415
"""GUI composition root — wires presentation-layer GUI services."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GuiServices:
    """Pre-wired services for the GUI layer."""

    db_path: Path
    database_manager: Any
    provider_routing: Any
    worker_manager: Any
    provider_config: Any = field(default=None, repr=False)
    user_preferences: Any = field(default=None, repr=False)
    usage_tracker: Any = field(default=None, repr=False)
    city_manager: Any = field(default=None, repr=False)
    weather_client: Any = field(default=None, repr=False)
    anomaly_profile_port: Any = field(default=None, repr=False)


def build_gui_services() -> GuiServices:
    """Build all GUI services with their dependencies wired up."""
    from src.config import DATA_DIR, ProviderConfig, UserPreferences, build_usage_tracker
    from src.infrastructure.container import (
        get_anomaly_profile_port,
        get_city_manager_port,
        get_weather_client_port,
    )
    from src.presentation.gui.controller.database_manager import DatabaseManager
    from src.presentation.gui.controller.provider_routing import ProviderRouting
    from src.presentation.gui.workers import WorkerManager

    db_path = DATA_DIR / "meteo_data.db"
    provider_config = ProviderConfig()
    user_preferences = UserPreferences()
    usage_tracker = build_usage_tracker()

    return GuiServices(
        db_path=db_path,
        database_manager=DatabaseManager(db_path),
        provider_config=provider_config,
        user_preferences=user_preferences,
        usage_tracker=usage_tracker,
        provider_routing=ProviderRouting(provider_config, user_preferences, usage_tracker),
        worker_manager=WorkerManager(),
        city_manager=get_city_manager_port(),
        weather_client=get_weather_client_port(),
        anomaly_profile_port=get_anomaly_profile_port(),
    )


__all__ = [
    "GuiServices",
    "build_gui_services",
]
