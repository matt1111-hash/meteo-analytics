"""Tab Manager - update and operations methods."""
from typing import Any, Optional


def update_standard_tabs(self, data: dict, city_name: str) -> None:
    """Szabványos tabok frissítése adatokkal."""
    # QuickOverviewTab
    if self.overview_tab and self._overview_available:
        self._logger.debug("QuickOverviewTab frissítése...")
        self.overview_tab.update_data(data, city_name)

    # DetailedChartsTab
    if self.charts_tab and self._charts_available:
        self._logger.debug("DetailedChartsTab frissítése...")
        self.charts_tab.update_data(data)

    # DataTableTab
    if self.table_tab and self._table_available:
        self._logger.debug("DataTableTab frissítése...")
        self.table_tab.update_data(data)

    # ExtremeEventsTab
    if self.extreme_tab and self._extreme_available:
        self._logger.debug("ExtremeEventsTab frissítése...")
        self.extreme_tab.update_data(data)


def update_windy_days_tab(self, data: Any, city_name: str, weather_df: Any) -> None:
    """WindyDaysTab frissítése adatokkal."""
    if not self.windy_days_tab:
        self._logger.error("WindyDaysTab nem elérhető!")
        return
    if not self._windy_days_available:
        self._logger.warning("WindyDaysTab fallback frissítése...")
        return

    self._logger.info("WindyDaysTab frissítése STARTED...")
    if not hasattr(self.windy_days_tab, 'update_data'):
        self._logger.error("WindyDaysTab.update_data metódus nem elérhető")
        return

    try:
        self.windy_days_tab.update_data(weather_df, city_name)
        self._logger.info("WindyDaysTab.update_data() SIKERES!")
    except Exception as e:
        self._logger.error(f"WindyDaysTab frissítési hiba: {e}")


def get_windy_days_tab(self) -> Optional[Any]:
    """WindyDaysTab referencia."""
    return self.windy_days_tab if self._windy_days_available else None


def get_charts_container(self) -> Optional[Any]:
    """Charts container referenciája."""
    if self.charts_tab and hasattr(self.charts_tab, 'charts_container'):
        return self.charts_tab.charts_container
    return None


def get_data_table(self) -> Optional[Any]:
    """Data table referenciája."""
    if self.table_tab and hasattr(self.table_tab, 'data_table'):
        return self.table_tab.data_table
    return None


def apply_theme(self, dark_theme: bool) -> None:
    """Téma alkalmazása az összes tab-ra."""
    if self.charts_tab and hasattr(self.charts_tab, 'apply_theme'):
        self.charts_tab.apply_theme(dark_theme)

    if self.table_tab and hasattr(self.table_tab, 'apply_theme'):
        self.table_tab.apply_theme(dark_theme)

    if self.windy_days_tab and hasattr(self.windy_days_tab, '_on_theme_changed'):
        theme_name = "dark" if dark_theme else "light"
        self.windy_days_tab._on_theme_changed(theme_name)


def clear_all_tabs(self) -> None:
    """Minden tab adatainak törlése."""
    if self.overview_tab and hasattr(self.overview_tab, '_clear_stats'):
        self.overview_tab._clear_stats()

    if self.charts_tab and hasattr(self.charts_tab, 'clear_data'):
        self.charts_tab.clear_data()

    if self.table_tab and hasattr(self.table_tab, 'clear_data'):
        self.table_tab.clear_data()

    if self.extreme_tab and hasattr(self.extreme_tab, '_clear_extremes'):
        self.extreme_tab._clear_extremes()

    if self.windy_days_tab and hasattr(self.windy_days_tab, 'clear_data'):
        self.windy_days_tab.clear_data()


def cleanup(self) -> None:
    """Tabok cleanup-ja."""
    if self.overview_tab and hasattr(self.overview_tab, 'cleanup'):
        self.overview_tab.cleanup()

    if self.charts_tab and hasattr(self.charts_tab, 'cleanup'):
        self.charts_tab.cleanup()

    if self.table_tab and hasattr(self.table_tab, 'cleanup'):
        self.table_tab.cleanup()

    if self.extreme_tab and hasattr(self.extreme_tab, 'cleanup'):
        self.extreme_tab.cleanup()

    if self.windy_days_tab and hasattr(self.windy_days_tab, 'cleanup'):
        self.windy_days_tab.cleanup()

    self._logger.debug("Tab cleanup completed")
