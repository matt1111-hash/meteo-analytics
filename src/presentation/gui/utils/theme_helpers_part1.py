# ruff: noqa: F403, F405
# mypy: ignore-errors
"""Merged part1 for StyleSheets."""

from __future__ import annotations

from .theme_helpers_part1_support import *
from .theme_helpers_support import *


class StyleSheetsPart1Mixin:  # noqa: D101
    @staticmethod
    def get_theme_stylesheet(theme_type: ThemeType) -> str:
        """
        Dynamic theme stylesheet via ThemeManager.

        Args:
            theme_type: Theme type

        Returns:
            Full application CSS stylesheet
        """
        try:
            # ThemeManager import (lazy to avoid circular dependency)
            from ..theme_manager import get_theme_manager  # noqa: PLC0415

            # ThemeManager singleton
            manager = get_theme_manager()

            # Set theme if different
            if manager.get_current_theme() != theme_type.value:
                manager.set_theme(theme_type.value)

            # Full application CSS generation
            css = StyleSheets._generate_full_application_css(manager, theme_type)

            logger.info(f"Dynamic theme stylesheet generated: {theme_type.value}")
            return css

        except ImportError as e:
            logger.warning(f"ThemeManager import failed, using legacy CSS: {e}")
            return StyleSheets._get_legacy_stylesheet(theme_type)
        except Exception as e:
            logger.error(f"ThemeManager CSS generation failed: {e}")
            return StyleSheets._get_legacy_stylesheet(theme_type)

    @staticmethod
    def _generate_full_application_css(manager, theme_type: ThemeType) -> str:  # noqa: ARG004
        """
        Full application CSS generation from ThemeManager components.

        Args:
            manager: ThemeManager instance
            theme_type: Theme type

        Returns:
            Complete CSS stylesheet
        """
        css_parts = []

        widget_types = [
            "container",
            "button",
            "input",
            "table",
            "scrollbar",
            "splitter",
            "navigation",
            "dialog",
            "chart",
        ]

        for widget_type in widget_types:
            try:
                widget_css = manager.generate_css_for_class(widget_type)
                if widget_css:
                    css_parts.append(f"/* {widget_type.upper()} WIDGETS */")
                    css_parts.append(widget_css)
                    css_parts.append("")
            except Exception as e:
                logger.warning(f"CSS generation failed for {widget_type}: {e}")

        return "\n".join(css_parts)

    @staticmethod
    def _get_legacy_stylesheet(theme_type: ThemeType) -> str:
        """Legacy CSS fallback when ThemeManager is unavailable."""
        if theme_type == ThemeType.DARK:
            return StyleSheets._LEGACY_DARK_THEME
        else:
            return StyleSheets._LEGACY_LIGHT_THEME

    @staticmethod
    def get_widget_stylesheet(widget_class: str, theme_type: Optional[ThemeType] = None) -> str:
        """
        Widget-specific CSS via ThemeManager.

        Args:
            widget_class: Widget type ("button", "input", "splitter", etc.)
            theme_type: Theme type, None for current

        Returns:
            Widget CSS stylesheet
        """
        try:
            from ..theme_manager import get_theme_manager  # noqa: PLC0415

            manager = get_theme_manager()

            if theme_type and manager.get_current_theme() != theme_type.value:
                manager.set_theme(theme_type.value)

            return manager.generate_css_for_class(widget_class)

        except Exception as e:
            logger.error(f"Widget CSS generation failed for {widget_class}: {e}")
            return ""

    @staticmethod
    def apply_theme_to_widget(
        widget, widget_class: str, theme_type: Optional[ThemeType] = None
    ) -> None:
        """
        Apply theme to a single widget via ThemeManager.

        Args:
            widget: Qt widget instance
            widget_class: Widget type
            theme_type: Theme type, None for current
        """
        try:
            from ..theme_manager import get_theme_manager  # noqa: PLC0415

            manager = get_theme_manager()
            manager.register_widget(widget, widget_class)

            logger.debug(f"Theme applied to widget: {widget.__class__.__name__} as {widget_class}")

        except Exception as e:
            logger.error(f"Widget theme application failed: {e}")

            # Fallback
            css = StyleSheets.get_widget_stylesheet(widget_class, theme_type)
            if css:
                widget.setStyleSheet(css)

    # === BACKWARD COMPATIBILITY PROPERTIES ===

    @property
    def LIGHT_THEME(self) -> str:
        """Backward compatibility - dynamic light theme."""
        return self.get_theme_stylesheet(ThemeType.LIGHT)


class StyleSheetsPart2Mixin:  # noqa: D101
    @property
    def DARK_THEME(self) -> str:
        """Backward compatibility - dynamic dark theme."""
        return self.get_theme_stylesheet(ThemeType.DARK)
