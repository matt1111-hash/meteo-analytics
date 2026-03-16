#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Provider Widget - Public API

🌐 Publikus interfész

Képességek:
- Provider beállítás
- Usage statisztikák kezelése
- State management
- Lifecycle metódusok

Fájl: src/presentation/gui/panel_widgets/provider_widget/public_api.py
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    pass


def set_provider(self, provider_name: str) -> None:
    """
    Provider beállítása külső hívásból.

    Args:
        self: ProviderWidget instance
        provider_name: Provider név
    """
    try:
        # Find and set provider in combo
        for i in range(self.provider_combo.count()):
            if self.provider_combo.itemData(i) == provider_name:
                self.provider_combo.setCurrentIndex(i)
                break

        print(f"✅ DEBUG: Provider set to: {provider_name}")

    except Exception as e:
        print(f"❌ DEBUG: Set provider error: {e}")


def get_current_provider(self) -> str:
    """
    Jelenlegi provider lekérdezése.

    Args:
        self: ProviderWidget instance

    Returns:
        str: Current provider name
    """
    return self.current_provider


def update_usage_stats(self, stats: Dict[str, Any]) -> None:
    """
    Usage statisztikák frissítése külső forrásból.

    Args:
        self: ProviderWidget instance
        stats: Usage statistics dictionary
    """
    try:
        from .monitoring import _update_usage_display

        self.usage_stats.update(stats)
        _update_usage_display(self)

        print(f"✅ DEBUG: Usage stats updated: {len(stats)} providers")

    except Exception as e:
        print(f"❌ DEBUG: Update usage stats error: {e}")


def get_usage_summary(self) -> Dict[str, Any]:
    """
    Usage összefoglaló lekérdezése.

    Args:
        self: ProviderWidget instance

    Returns:
        Dict[str, Any]: Usage summary
    """
    total_requests = sum(
        stats.get("requests", 0) for stats in self.usage_stats.values()
    )
    total_cost = sum(
        stats.get("estimated_cost", 0) for stats in self.usage_stats.values()
    )

    return {
        "current_provider": self.current_provider,
        "total_requests": total_requests,
        "total_cost": total_cost,
        "provider_stats": self.usage_stats.copy(),
    }


def stop_monitoring(self) -> None:
    """
    Monitoring leállítása.

    Args:
        self: ProviderWidget instance
    """
    if self.usage_timer.isActive():
        self.usage_timer.stop()
        print("🛑 DEBUG: Usage monitoring stopped")


def start_monitoring(self) -> None:
    """
    Monitoring indítása.

    Args:
        self: ProviderWidget instance
    """
    if not self.usage_timer.isActive():
        self.usage_timer.start()
        print("🔄 DEBUG: Usage monitoring started")


def get_state(self) -> Dict[str, Any]:
    """
    Widget állapot lekérdezése.

    Args:
        self: ProviderWidget instance

    Returns:
        Dict[str, Any]: Widget state
    """
    return {
        "current_provider": self.current_provider,
        "provider_preferences": {
            "default_provider": "open-meteo",  # OPEN-METEO alapértelmezett
            "auto_fallback": False,  # Auto routing letiltva alapértelmezetten
        },
        "is_valid": is_valid(self),
    }


def set_state(self, state: Dict[str, Any]) -> bool:
    """
    Widget állapot beállítása.

    Args:
        self: ProviderWidget instance
        state: Widget state dictionary

    Returns:
        bool: True ha sikeres
    """
    try:
        provider = state.get("current_provider", "open-meteo")  # Fallback to Open-Meteo
        set_provider(self, provider)

        print(f"✅ DEBUG: ProviderWidget state set: {provider}")
        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to set ProviderWidget state: {e}")
        return False


def is_valid(self) -> bool:
    """
    Widget validálása - mindig valid (van alapértelmezett provider).

    Args:
        self: ProviderWidget instance

    Returns:
        bool: Always True
    """
    return True


def set_enabled(self, enabled: bool) -> None:
    """
    Widget engedélyezése/letiltása.

    Args:
        self: ProviderWidget instance
        enabled: Enabled flag
    """
    self.provider_combo.setEnabled(enabled)

    print(f"🌍 DEBUG: ProviderWidget enabled state: {enabled}")


def refresh_usage_display(self) -> None:
    """
    Usage display frissítése (external API).

    Args:
        self: ProviderWidget instance
    """
    from .monitoring import _update_usage_display

    _update_usage_display(self)


def cleanup(self) -> None:
    """
    Widget cleanup.

    Args:
        self: ProviderWidget instance
    """
    stop_monitoring(self)
    print("🧹 DEBUG: ProviderWidget cleanup completed")


def closeEvent(self, event) -> None:
    """
    Widget bezárása.

    Args:
        self: ProviderWidget instance
        event: Close event
    """
    cleanup(self)
    from PySide6.QtWidgets import QWidget

    QWidget.closeEvent(self, event)
