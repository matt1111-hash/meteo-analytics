# mypy: ignore-errors
"""Theme, settings, and view helpers for the main window."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QSplitter

from ..utils import ThemeType
from .main_window_actions import switch_view

if TYPE_CHECKING:
    from .main_window import MainWindow


class MainWindowThemeSettingsMixin:
    """Helpers for provider status, themes, and settings persistence."""

    def _initialize_provider_status(self: "MainWindow") -> None:
        """Initialize provider status from settings."""
        self.state.provider.current_provider = self.settings.value(
            "current_provider",
            "auto",
        )
        self._update_provider_status_display()

    def _update_provider_status_display(self: "MainWindow") -> None:
        """Refresh provider status widgets."""
        if self.provider_status_label:
            self.provider_status_label.setText(
                f"Provider: {self.state.provider.current_provider}"
            )
        if self.usage_status_label and self.state.provider.provider_usage_stats:
            usage = self.state.provider.provider_usage_stats.get(
                self.state.provider.current_provider,
                {},
            )
            daily = usage.get("daily_requests", 0)
            self.usage_status_label.setText(f"Használat: {daily}/1000")

    def _on_theme_manager_changed(self: "MainWindow", theme_name: str) -> None:
        """Handle theme manager updates."""
        try:
            self.state.current_theme = ThemeType(theme_name)
        except ValueError:
            self.state.current_theme = ThemeType.LIGHT

        if self.stacked_widget and self.stacked_widget.count() > 0:
            single_city_view = self.stacked_widget.widget(0)
            if single_city_view:
                for splitter in single_city_view.findChildren(QSplitter):
                    splitter_css = self.theme_manager.generate_css_for_class("splitter")
                    splitter.setStyleSheet(splitter_css)

    def _apply_theme(self: "MainWindow", theme_type: ThemeType) -> None:
        """Apply the selected theme."""
        self.theme_manager.set_theme(theme_type.value)

    def _apply_theme_internal(self: "MainWindow", theme_type: ThemeType) -> None:
        """Apply a theme and keep it in state."""
        self.state.current_theme = theme_type
        self.theme_manager.set_theme(theme_type.value)

    def _theme_from_str(self: "MainWindow", theme_str: str) -> ThemeType:
        """Convert raw theme values to ThemeType."""
        try:
            return ThemeType(theme_str)
        except ValueError:
            return ThemeType.LIGHT

    def _save_settings(self: "MainWindow") -> None:
        """Persist window settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("current_view", self.state.current_view_name)
        self.settings.setValue("theme", self.state.current_theme.value)
        self.theme_manager.save_theme_preferences(self.settings)
        self.settings.setValue("current_provider", self.state.provider.current_provider)

    def _load_settings(self: "MainWindow") -> None:
        """Load persisted window settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        theme_name = self.settings.value("theme", "light")
        try:
            self._apply_theme_internal(ThemeType(theme_name))
        except ValueError:
            self._apply_theme_internal(ThemeType.LIGHT)

        self._initialize_provider_status()
        switch_view(self, "single_city")

    def _switch_view(self: "MainWindow", view_name: str) -> None:
        """Switch the active stacked view."""
        switch_view(self, view_name)
