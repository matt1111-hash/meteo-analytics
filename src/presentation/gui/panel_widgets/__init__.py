#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Universal Weather Research Platform - Panel Widgets Package
🎯 CLEAN ARCHITECTURE REFAKTOR - Widget Components

Ez a package tartalmazza a refaktorált ControlPanel widget komponenseit.
Minden widget a Single Responsibility elvét követi és clean interface-t biztosít.

Widget komponensek:
- AnalysisTypeWidget: Elemzési típus választó (Egyedi/Régió/Megye)
- LocationWidget: Lokáció választó (UniversalLocationSelector wrapper)
- DateRangeWidget: Dátum tartomány (Multi-year + Manual modes)
- ProviderWidget: API provider választó + Usage tracking
- ApiSettingsWidget: API beállítások (Timeout, Cache, Timezone)
- QueryControlWidget: Lekérdezés vezérlő (Fetch/Cancel + Progress) - MEGLÉVŐ

Minden widget interface:
- get_state() -> dict: Aktuális állapot lekérdezése
- set_state(dict) -> bool: Állapot beállítása
- is_valid() -> bool: Validáció
- set_enabled(bool): Widget engedélyezése/letiltása
- Megfelelő signalok a változások jelzésére
"""

# Widget komponensek
from .analysis_type_widget import AnalysisTypeWidget
from .api_settings_widget import ApiSettingsWidget
from .date_range_widget import DateRangeWidget
from .location_widget import LocationWidget
from .provider_widget import ProviderWidget
from .query_control_widget import QueryControlWidget  # MEGLÉVŐ widget

# Package információk
__version__ = "1.0.0"
__author__ = "Universal Weather Research Platform Team"

# Exportált komponensek
__all__ = [
    "AnalysisTypeWidget",
    "LocationWidget",
    "DateRangeWidget",
    "ProviderWidget",
    "ApiSettingsWidget",
    "QueryControlWidget",
]


# Widget factory funkciók (opcionális, könnyebb használathoz)
def create_analysis_type_widget(parent=None) -> AnalysisTypeWidget:
    """AnalysisTypeWidget factory."""
    return AnalysisTypeWidget(parent)


def create_location_widget(city_manager, parent=None) -> LocationWidget:
    """LocationWidget factory."""
    return LocationWidget(city_manager, parent)


def create_date_range_widget(parent=None) -> DateRangeWidget:
    """DateRangeWidget factory."""
    return DateRangeWidget(parent)


def create_provider_widget(parent=None) -> ProviderWidget:
    """ProviderWidget factory."""
    return ProviderWidget(parent)


def create_api_settings_widget(parent=None) -> ApiSettingsWidget:
    """ApiSettingsWidget factory."""
    return ApiSettingsWidget(parent)


def create_query_control_widget(parent=None) -> QueryControlWidget:
    """QueryControlWidget factory."""
    return QueryControlWidget(parent)


# Widget state validation helper
def validate_widget_states(*widgets) -> bool:
    """
    Több widget állapotának validálása egyszerre.

    Args:
        *widgets: Widget instances

    Returns:
        bool: True ha minden widget valid
    """
    return all(widget.is_valid() for widget in widgets if hasattr(widget, "is_valid"))


# Widget state aggregation helper
def get_all_widget_states(*widgets) -> dict:
    """
    Több widget állapotának összegyűjtése.

    Args:
        *widgets: Widget instances

    Returns:
        dict: Összes widget state aggregálva
    """
    states = {}
    for i, widget in enumerate(widgets):
        if hasattr(widget, "get_state"):
            widget_name = widget.__class__.__name__
            states[widget_name] = widget.get_state()
        else:
            states[f"widget_{i}"] = None

    return states


# Debug helper
def print_widget_info(*widgets) -> None:
    """
    Widget információk debug kiírása.

    Args:
        *widgets: Widget instances
    """
    print("🎯 DEBUG: Panel Widgets Info:")
    for widget in widgets:
        widget_name = widget.__class__.__name__
        valid = widget.is_valid() if hasattr(widget, "is_valid") else "Unknown"
        print(f"  - {widget_name}: valid={valid}")


print("🎯 DEBUG: Panel Widgets package loaded - Clean Architecture Components")
