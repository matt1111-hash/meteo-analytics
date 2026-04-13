#!/usr/bin/env python3
# mypy: ignore-errors

"""
ThemeManager Theme Appliers - Different theme application strategies.
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QPalette

if TYPE_CHECKING:
    from .core import ProfessionalThemeManager


def apply_qdarktheme_theme(theme_name: str, manager: "ProfessionalThemeManager") -> None:
    """
    Apply qdarktheme (professional) theme.

    Args:
        theme_name: Theme name ("light" or "dark")
        manager: ThemeManager instance
    """
    import qdarktheme  # noqa: PLC0415

    qdarktheme.setup_theme(theme_name)
    _enhance_with_color_palette(manager)


def apply_qt6_native_theme(theme_name: str, manager: "ProfessionalThemeManager") -> None:
    """
    Apply Qt6.5+ native ColorScheme theme.

    Args:
        theme_name: Theme name ("light" or "dark")
        manager: ThemeManager instance
    """
    from PySide6.QtGui import QGuiApplication, Qt  # noqa: PLC0415

    if theme_name == "dark":
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    else:
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)

    _enhance_with_color_palette(manager)


def apply_color_palette_theme(
    theme_name: str,  # noqa: ARG001
    manager: "ProfessionalThemeManager",
) -> None:
    """
    Apply ColorPalette-based theme (fallback).

    Args:
        theme_name: Theme name ("light" or "dark")
        manager: ThemeManager instance
    """
    if not manager.app:
        raise Exception("QApplication not available for professional theming")

    palette = QPalette()
    colors = manager.get_current_colors()

    # Professional color mapping
    palette.setColor(QPalette.ColorRole.Window, QColor(colors["surface"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["on_surface"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface_variant"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["surface_variant"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["surface"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["on_surface"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["on_surface"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["surface_variant"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["on_surface"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["error"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(colors["info"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["on_surface"]))

    # Professional disabled state
    disabled_group = QPalette.ColorGroup.Disabled
    disabled_text = QColor(colors["on_surface"])
    disabled_text.setAlpha(100)  # 40% opacity
    palette.setColor(disabled_group, QPalette.ColorRole.WindowText, disabled_text)
    palette.setColor(disabled_group, QPalette.ColorRole.Text, disabled_text)
    palette.setColor(disabled_group, QPalette.ColorRole.ButtonText, disabled_text)

    manager.app.setPalette(palette)


def _enhance_with_color_palette(manager: "ProfessionalThemeManager") -> None:
    """
    Enhance Qt theming with ColorPalette colors.

    Args:
        manager: ThemeManager instance
    """
    if not manager.app:
        return

    palette = manager.app.palette()
    colors = manager.get_current_colors()

    # 🎨 PIROS (#C43939) TÉMA enhancement
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(colors["info"]))

    # Weather-specific enhancements
    if hasattr(manager, "weather_palette"):
        weather_colors = manager.weather_palette.get_all_variants("primary")
        if "hover" in weather_colors:
            hover_color = QColor(weather_colors["hover"])
            palette.setColor(QPalette.ColorRole.Highlight, hover_color)

    manager.app.setPalette(palette)
