#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provider selector configuration and user preferences management."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, TypeVar, cast

from src.config.paths_config import (
    PROVIDER_PREFS_FILE as DEFAULT_PROVIDER_PREFS_FILE,
    ensure_directories as default_ensure_directories,
)

LOGGER = logging.getLogger(__name__)
T = TypeVar("T")


def _resolve_config_attr(attr: str, fallback: T) -> T:
    """Return config module attribute if tests monkeypatch it."""
    config_module = sys.modules.get("src.config")
    if config_module and hasattr(config_module, attr):
        return cast(T, getattr(config_module, attr))
    return fallback


def _get_provider_prefs_file() -> Path:
    """Return current provider preferences path."""
    return _resolve_config_attr("PROVIDER_PREFS_FILE", DEFAULT_PROVIDER_PREFS_FILE)


def _ensure_directories() -> None:
    """Invoke the potentially monkeypatched ensure_directories helper."""
    resolver = _resolve_config_attr("ensure_directories", default_ensure_directories)
    resolver()


def _freeze_value(value: Any) -> Any:
    """Recursively freeze nested provider metadata structures."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_value(val) for key, val in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    return value


class ProviderConfig:
    """Provider Selector configuration and settings."""

    _PROVIDER_DATA: Dict[str, Dict[str, Any]] = {
        "auto": {
            "name": "Automatikus (Smart Routing)",
            "description": "Use-case alapú automatikus provider választás",
            "icon": "🤖",
            "cost": "Optimalizált",
            "routing_logic": {
                "single_city": "open-meteo",
                "multi_city": "meteostat",
                "historical_deep": "meteostat",
                "real_time": "open-meteo",
            },
        },
        "open-meteo": {
            "name": "Open-Meteo (Ingyenes)",
            "description": "Ingyenes globális időjárási API minden funkcióhoz",
            "icon": "🌍",
            "cost": "Ingyenes",
            "limitations": [
                "Limitált multi-city support",
                "Alapszintű történeti adatok",
            ],
        },
        "meteostat": {
            "name": "Meteostat (Prémium)",
            "description": "Prémium API gazdag történeti adatokkal és station-based accuracy",
            "icon": "💎",
            "cost": "$10 USD/hónap",
            "features": [
                "10k request/hónap",
                "Gazdag történeti adatok",
                "Station-based accuracy",
            ],
        },
    }

    PROVIDERS: Mapping[str, Mapping[str, Any]] = MappingProxyType(
        {key: _freeze_value(value) for key, value in _PROVIDER_DATA.items()}
    )

    DEFAULT_PROVIDER: str = "auto"
    USAGE_RESET_DAY: int = 1
    WARNING_THRESHOLD: float = 0.8
    CRITICAL_THRESHOLD: float = 0.95
    METEOSTAT_COST_PER_REQUEST: float = 0.001
    MONTHLY_BUDGET_USD: float = 10.0


class UserPreferences:
    """User preferences management for Provider Selector."""

    @staticmethod
    def load_provider_preferences() -> Dict[str, Any]:
        """
        Load user's provider preferences from file.

        Returns:
            Dictionary with user preferences
        """
        default_prefs = {
            "selected_provider": ProviderConfig.DEFAULT_PROVIDER,
            "auto_fallback_enabled": True,
            "show_usage_warnings": True,
            "show_cost_estimates": True,
            "monthly_budget_usd": ProviderConfig.MONTHLY_BUDGET_USD,
            "warning_threshold": ProviderConfig.WARNING_THRESHOLD,
            "last_updated": datetime.now().isoformat()
        }

        prefs_file = _get_provider_prefs_file()

        try:
            if prefs_file.exists():
                with open(prefs_file, "r", encoding="utf-8") as file_obj:
                    prefs = json.load(file_obj)
                    return {**default_prefs, **prefs}
            return default_prefs
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Provider preferences betöltése sikertelen", exc_info=exc)
            return default_prefs

    @staticmethod
    def save_provider_preferences(preferences: Dict[str, Any]) -> bool:
        """
        Save user's provider preferences to file.

        Args:
            preferences: Dictionary with user preferences

        Returns:
            True if saved successfully, False otherwise
        """
        prefs_file = _get_provider_prefs_file()

        try:
            _ensure_directories()
            preferences["last_updated"] = datetime.now().isoformat()

            with open(prefs_file, "w", encoding="utf-8") as file_obj:
                json.dump(preferences, file_obj, indent=2, ensure_ascii=False)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Provider preferences mentése sikertelen", exc_info=exc)
            return False

    @staticmethod
    def get_selected_provider() -> str:
        """Get user's currently selected provider."""
        prefs = UserPreferences.load_provider_preferences()
        selected = prefs.get("selected_provider", ProviderConfig.DEFAULT_PROVIDER)
        return str(selected)

    @staticmethod
    def set_selected_provider(provider: str) -> bool:
        """
        Set user's selected provider.

        Args:
            provider: Provider name ("auto", "open-meteo", "meteostat")

        Returns:
            True if set successfully, False otherwise
        """
        if provider not in ProviderConfig.PROVIDERS:
            return False

        prefs = UserPreferences.load_provider_preferences()
        prefs["selected_provider"] = provider
        return UserPreferences.save_provider_preferences(prefs)

    @staticmethod
    def get_provider_info(provider: str) -> Dict[str, Any] | None:
        """
        Get provider information by name.

        Args:
            provider: Provider name

        Returns:
            Provider info dictionary or None if not found
        """
        provider_data = ProviderConfig.PROVIDERS.get(provider)
        if provider_data is None:
            return None
        return dict(provider_data)

    @staticmethod
    def list_available_providers() -> Dict[str, Dict[str, Any]]:
        """
        Get list of all available providers.

        Returns:
            Dictionary of all providers with their info
        """
        return {key: dict(value) for key, value in ProviderConfig.PROVIDERS.items()}


def get_resolved_provider(use_case: str, user_override: Optional[str] = None) -> str:
    """
    Get resolved provider for specific use case.

    Args:
        use_case: Use case ("single_city", "multi_city", "historical_deep", "real_time")
        user_override: User's provider preference override

    Returns:
        Resolved provider name
    """
    # User override has highest priority
    if user_override and user_override != "auto":
        return user_override

    # Get user's selected provider
    selected_provider = UserPreferences.get_selected_provider()

    if selected_provider == "auto":
        # Use smart routing
        routing = ProviderConfig.PROVIDERS["auto"]["routing_logic"]
        selected = routing.get(use_case, "open-meteo")
        return str(selected)
    else:
        # Use user's fixed selection
        return selected_provider


def validate_provider_selection(provider: str) -> bool:
    """
    Validate that a provider is supported.

    Args:
        provider: Provider name to validate

    Returns:
        True if provider is valid, False otherwise
    """
    return provider in ProviderConfig.PROVIDERS
