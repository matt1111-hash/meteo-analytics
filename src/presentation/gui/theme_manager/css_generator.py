#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
ThemeManager CSS Generator - Dynamic CSS generation for widgets.
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .core import ProfessionalThemeManager


class CSSGenerator:
    """Professional CSS generation from ColorPalette."""

    def __init__(self, manager: "ProfessionalThemeManager"):
        """
        Initialize CSS generator.

        Args:
            manager: ThemeManager instance
        """
        self._manager = manager
        self._css_class_cache: Dict[str, str] = {}

    def clear_cache(self) -> None:
        """Clear CSS cache for regeneration."""
        self._css_class_cache.clear()

    def get_cache_size(self) -> int:
        """Get current cache size."""
        return len(self._css_class_cache)

    def generate_css_for_class(self, css_class: str) -> str:
        """
        Generate professional CSS for a widget class.

        Args:
            css_class: CSS class name (e.g., "QPushButton", "QTabWidget", "splitter")

        Returns:
            Professional CSS string with ColorPalette integration
        """
        # Check cache first
        cache_key = f"{css_class}_{self._manager.current_theme}"
        if cache_key in self._css_class_cache:
            return self._css_class_cache[cache_key]

        colors = self._manager.get_current_colors()

        # Professional CSS templates
        css_templates = {
            "QPushButton": self._generate_pushbutton_css(colors),
            "QTabWidget": self._generate_tabwidget_css(colors),
            "splitter": self._generate_splitter_css(colors),
            "QScrollBar": self._generate_scrollbar_css(colors),
            "analytics_panel": self._generate_analytics_panel_css(colors),
        }

        # Generate CSS
        css = css_templates.get(css_class, "")

        # Cache the result
        self._css_class_cache[cache_key] = css

        return css

    def _generate_pushbutton_css(self, colors: Dict[str, str]) -> str:
        """Generate QPushButton CSS."""
        return f"""
                QPushButton {{
                    background-color: {colors["surface_variant"]};
                    color: {colors["on_surface"]};
                    border: 1px solid {colors["border"]};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {colors["hover_overlay"]};
                }}
                QPushButton:pressed {{
                    background-color: {colors["primary"]};
                    color: {colors["surface"]};
                }}
                QPushButton:disabled {{
                    background-color: {colors["surface_variant"]};
                    color: {colors["info"]};
                    opacity: 0.6;
                }}
            """

    def _generate_tabwidget_css(self, colors: Dict[str, str]) -> str:
        """Generate QTabWidget CSS."""
        return f"""
                QTabWidget::pane {{
                    background-color: {colors["surface"]};
                    border: 1px solid {colors["border"]};
                    border-radius: 4px;
                }}
                QTabWidget::tab-bar {{
                    left: 5px;
                }}
                QTabBar::tab {{
                    background-color: {colors["surface_variant"]};
                    color: {colors["on_surface"]};
                    border: 1px solid {colors["border"]};
                    border-bottom-color: transparent;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {colors["primary"]};
                    color: {colors["surface"]};
                }}
                QTabBar::tab:hover {{
                    background-color: {colors["hover_overlay"]};
                }}
            """

    def _generate_splitter_css(self, colors: Dict[str, str]) -> str:
        """Generate QSplitter CSS."""
        return f"""
                QSplitter::handle {{
                    background-color: {colors["border"]};
                    border: 1px solid {colors["surface_variant"]};
                }}
                QSplitter::handle:horizontal {{
                    width: 3px;
                    margin: 0 2px;
                }}
                QSplitter::handle:vertical {{
                    height: 3px;
                    margin: 2px 0;
                }}
                QSplitter::handle:hover {{
                    background-color: {colors["primary"]};
                }}
            """

    def _generate_scrollbar_css(self, colors: Dict[str, str]) -> str:
        """Generate QScrollBar CSS."""
        return f"""
                QScrollBar:vertical {{
                    background-color: {colors["surface_variant"]};
                    width: 12px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {colors["info"]};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {colors["primary"]};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """

    def _generate_analytics_panel_css(self, colors: Dict[str, str]) -> str:
        """Generate analytics panel CSS."""
        return f"""
                QWidget#analytics_panel {{
                    background-color: {colors["surface"]};
                    border: 1px solid {colors["border"]};
                    border-radius: 8px;
                }}
                QLabel#analytics_title {{
                    color: {colors["on_surface"]};
                    font-size: 16px;
                    font-weight: 600;
                }}
                QGroupBox#analytics_group {{
                    color: {colors["on_surface"]};
                    border: 2px solid {colors["border"]};
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 8px;
                }}
                QGroupBox#analytics_group::title {{
                    color: {colors["primary"]};
                    font-weight: 600;
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px 0 4px;
                }}
            """
