# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from public_api.py."""

from __future__ import annotations

from .public_api_support import *


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
    if windy_days_tab and hasattr(windy_days_tab, "_start_analysis"):
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
    print(
        f"🚨 DEBUG: data type={type(data)}, keys={list(data.keys()) if isinstance(data, dict) else 'NEM DICT'}"
    )
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
            lambda df, city: self.tab_manager.update_windy_days_tab(data, city, df),
        )

    except Exception as convert_error:
        logger.error(f"🚨 DEBUG: _convert_data_to_dataframe() HIBA: {convert_error}")
        import traceback

        traceback.print_exc()
        empty_df = self.data_processor._empty_dataframe_fallback()
        self.tab_manager.update_windy_days_tab(data, city_name, empty_df)
