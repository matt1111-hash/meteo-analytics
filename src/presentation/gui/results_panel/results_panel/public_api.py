#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results Panel - Public API

🌐 Publikus interfész

Képességek:
- Progress API
- Tab API
- Data update API
- Getter methods
- Theme handling

Fájl: src/presentation/gui/results_panel/results_panel/public_api.py
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# === PROGRESS API ===

def show_loading_indicator(self, message: str = "⏳ Adatok betöltése...") -> None:
    """Loading indicator megjelenítése."""
    self.progress_manager.show_loading(message)


def hide_loading_indicator(self) -> None:
    """Loading indicator elrejtése."""
    self.progress_manager.hide_loading()


def update_loading_progress(self, message: str) -> None:
    """Loading progress frissítése."""
    self.progress_manager.update_progress(message)


def force_hide_loading(self) -> None:
    """Loading indicator kényszerített elrejtése."""
    self.progress_manager.force_hide()


def is_loading(self) -> bool:
    """Loading állapot lekérdezése."""
    return self.progress_manager.is_loading()


def get_loading_status(self) -> Dict[str, Any]:
    """Loading állapot részletes lekérdezése."""
    return {
        "is_loading": self.is_loading(),
        "progress_text": self.progress_manager.get_progress_text(),
        "progress_visible": self.progress_indicator.isVisible(),
    }


# === TAB API ===

def switch_to_tab(self, tab_name: str) -> None:
    """Specifikus tab-ra váltás."""
    self.tab_manager.switch_to_tab(tab_name)


def get_current_tab(self) -> str:
    """Jelenlegi aktív tab nevének lekérdezése."""
    return self.tab_manager.get_current_tab()


def switch_to_windy_days_tab(self) -> None:
    """Szeles napok tab-ra váltás."""
    self.switch_to_tab("windy_days")


def get_windy_days_tab(self):
    """WindyDaysTab referencia lekérdezése."""
    return self.tab_manager.get_windy_days_tab()


def trigger_windy_days_analysis(self) -> None:
    """Szeles napok analízis programatikus triggerelése."""
    windy_days_tab = self.get_windy_days_tab()
    if windy_days_tab and hasattr(windy_days_tab, '_start_analysis'):
        windy_days_tab._start_analysis()
        logger.info("🌪️ WindyDaysTab analízis programatikusan triggerelve")


# === DATA UPDATE API ===

def update_data(self, data: Dict[str, Any], city_name: str) -> None:
    """
    Adatok frissítése.

    Args:
        self: ResultsPanel instance
        data: OpenMeteo API válasz
        city_name: Város neve
    """
    print("=" * 80)
    print("🚨 DEBUG: ResultsPanel.update_data() ELEJE")
    print(f"🚨 DEBUG: city_name={city_name}")
    print(f"🚨 DEBUG: data type={type(data)}, keys={list(data.keys()) if isinstance(data, dict) else 'NEM DICT'}")
    print("=" * 80)

    logger.info(f"ResultsPanel.update_data() - City: {city_name} (REFACTORED)")

    try:
        # Loading elrejtése ha aktív
        if self.is_loading():
            self.hide_loading_indicator()

        # Állapot mentése
        self.current_data = data
        self.current_city = city_name
        _update_title(self, city_name)

        # Szabványos tabok frissítése
        self.tab_manager.update_standard_tabs(data, city_name)

        # WindyDaysTab frissítése
        _update_windy_days_tab(self, data, city_name)

        # Signal küldése
        self.data_updated.emit(data, city_name)
        logger.info("ResultsPanel.update_data() SIKERES!")

    except Exception as e:
        logger.error(f"ResultsPanel adatfrissítési hiba: {e}")
        import traceback
        traceback.print_exc()

        # Error esetén is hide loading
        if self.is_loading():
            self.hide_loading_indicator()

        # Error message megjelenítése
        self.title_label.setText(f"❌ Adatfrissítési hiba: {str(e)[:50]}...")
        clear_data(self)


def _update_title(self, city_name: str) -> None:
    """Title frissítése város névvel."""
    self.title_label.setText(f"📊 Időjárási Adatok - {city_name}")


def _update_windy_days_tab(self, data: Dict[str, Any], city_name: str) -> None:
    """WindyDaysTab frissítése."""
    logger.info("🌪️ WindyDaysTab frissítése STARTED (REFACTORED)...")

    try:
        # DataFrame konverzió
        weather_df = self.data_processor.convert_data_to_dataframe(data)
        logger.info("🚨 DEBUG: _convert_data_to_dataframe() HÍVÁS SIKERES")

        # Adatok kézbesítése
        self.data_processor.process_windy_days_data(
            weather_df,
            city_name,
            lambda df, city: self.tab_manager.update_windy_days_tab(data, city, df)
        )

    except Exception as convert_error:
        logger.error(f"🚨 DEBUG: _convert_data_to_dataframe() HIBA: {convert_error}")
        import traceback
        traceback.print_exc()
        empty_df = self.data_processor._empty_dataframe_fallback()
        self.tab_manager.update_windy_days_tab(data, city_name, empty_df)


def clear_data(self) -> None:
    """Adatok törlése."""
    logger.debug("ResultsPanel.clear_data() MEGHÍVVA")

    # Loading elrejtése
    if self.is_loading():
        self.hide_loading_indicator()

    # Állapot törlése
    self.current_data = None
    self.current_city = None

    # Title reset
    self.title_label.setText("📊 Időjárási Adatok Elemzése")

    # Tabok törlése
    self.tab_manager.clear_all_tabs()

    logger.debug("ResultsPanel.clear_data() BEFEJEZVE")


# === EXTREME WEATHER ===

def trigger_extreme_weather_analysis(self) -> None:
    """Programmatic extreme weather trigger."""
    logger.info("🔥 Programmatic extreme weather analysis triggered")
    self.extreme_weather_requested.emit()


# === PUBLIKUS GETTEREK ===

def get_charts_container(self):
    """Charts container referenciájának lekérdezése."""
    return self.tab_manager.get_charts_container()


def get_data_table(self):
    """Data table referenciájának lekérdezése."""
    return self.tab_manager.get_data_table()


# === TÉMA KEZELÉS ===

def apply_theme(self, dark_theme: bool) -> None:
    """
    Téma alkalmazása.

    Args:
        self: ResultsPanel instance
        dark_theme: Sötét téma engedélyezve
    """
    logger.debug(f"ResultsPanel.apply_theme({dark_theme}) MEGHÍVVA")
    self.tab_manager.apply_theme(dark_theme)
    logger.debug("ResultsPanel.apply_theme() BEFEJEZVE")


def apply_theme_by_name(self, theme_name: str) -> None:
    """Téma alkalmazása név alapján."""
    if self.theme_manager:
        success = self.theme_manager.set_theme(theme_name)
        if success:
            logger.info(f"ResultsPanel téma alkalmazva: {theme_name}")
        else:
            logger.error(f"ResultsPanel téma alkalmazás sikertelen: {theme_name}")


def get_current_theme_name(self) -> str:
    """Jelenlegi téma nevének lekérdezése."""
    if self.theme_manager:
        return self.theme_manager.get_current_theme()
    return "default"
