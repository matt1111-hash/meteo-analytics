# mypy: ignore-errors
"""Tab Manager - re-export for backward compatibility."""

from src.presentation.gui.results_panel.tab_manager.core import TabManager

# Add update methods to TabManager class
from src.presentation.gui.results_panel.tab_manager.updaters import (
    apply_theme,
    cleanup,
    clear_all_tabs,
    get_charts_container,
    get_data_table,
    get_windy_days_tab,
    update_standard_tabs,
    update_windy_days_tab,
)

TabManager.update_standard_tabs = update_standard_tabs
TabManager.update_windy_days_tab = update_windy_days_tab
TabManager.get_windy_days_tab = get_windy_days_tab
TabManager.get_charts_container = get_charts_container
TabManager.get_data_table = get_data_table
TabManager.apply_theme = apply_theme
TabManager.clear_all_tabs = clear_all_tabs
TabManager.cleanup = cleanup

__all__ = ["TabManager"]
