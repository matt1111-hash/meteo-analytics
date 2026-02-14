#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI Theme Helpers Module.
Témakezelés és stíluslap generálás.

🎨 THEMEMANAGER INTEGRÁCIÓ:
✅ Dinamikus CSS generálás ThemeManager-rel
✅ ColorPalette support
✅ Runtime téma váltás
✅ Backward compatibility
✅ Widget-specifikus styling support
"""

import logging
from typing import Optional

from src.presentation.gui.types import ThemeType

logger = logging.getLogger(__name__)


class StyleSheets:
    """
    PySide6 stíluslapok - THEMEMANAGER INTEGRÁLT VERZIÓ.

    🎨 VÁLTOZÁSOK V2.1:
    ✅ Dinamikus CSS generálás ThemeManager-rel
    ✅ ColorPalette színek használata
    ✅ Legacy CSS-ek fallback-ként megtartva
    ✅ Widget-specifikus styling support
    ✅ Runtime téma váltás támogatás
    ✅ Dual-API source styling
    """

    # === LEGACY SUPPORT - STATIKUS CSS-EK FALLBACK-KÉNT ===

    # LEGACY LIGHT THEME - csak fallback célokra
    _LEGACY_LIGHT_THEME = """
        QMainWindow, QWidget {
            background-color: #ffffff;
            color: #1f2937;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }

        QPushButton {
            background-color: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 20px;
        }

        QPushButton:hover {
            background-color: #e5e7eb;
            border-color: #9ca3af;
        }

        QPushButton:pressed {
            background-color: #d1d5db;
        }

        QSplitter::handle {
            background-color: #e5e7eb;
            border: 1px solid #d1d5db;
        }

        QSplitter::handle:horizontal {
            width: 8px;
            margin: 2px 0px;
        }

        QSplitter::handle:pressed {
            background-color: #2563eb;
        }
    """

    # LEGACY DARK THEME - csak fallback célokra
    _LEGACY_DARK_THEME = """
        QMainWindow, QWidget {
            background-color: #1f2937;
            color: #f9fafb;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }

        QPushButton {
            background-color: #374151;
            border: 1px solid #4b5563;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 20px;
            color: #f9fafb;
        }

        QPushButton:hover {
            background-color: #4b5563;
            border-color: #6b7280;
        }

        QPushButton:pressed {
            background-color: #1e40af;
            border-color: #3b82f6;
        }

        QSplitter::handle {
            background-color: #4b5563;
            border: 1px solid #6b7280;
        }

        QSplitter::handle:horizontal {
            width: 8px;
            margin: 2px 0px;
        }

        QSplitter::handle:pressed {
            background-color: #3b82f6;
        }
    """

    # === ÚJ: THEMEMANAGER INTEGRÁCIÓ ===

    @staticmethod
    def get_theme_stylesheet(theme_type: ThemeType) -> str:
        """
        🎨 DINAMIKUS téma stylesheet lekérdezése ThemeManager-rel.

        Args:
            theme_type: Téma típusa

        Returns:
            Teljes alkalmazás CSS stylesheet
        """
        try:
            # 🎨 THEMEMANAGER IMPORTÁLÁS (lazy import circular dependency elkerülésére)
            from ..theme_manager import get_theme_manager

            # ThemeManager singleton lekérdezése
            manager = get_theme_manager()

            # Téma beállítása ha nem egyezik
            if manager.get_current_theme() != theme_type.value:
                manager.set_theme(theme_type.value)

            # Teljes alkalmazás CSS generálása
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
    def _generate_full_application_css(manager, theme_type: ThemeType) -> str:
        """
        Teljes alkalmazás CSS generálása ThemeManager komponensekből.

        Args:
            manager: ThemeManager instance
            theme_type: Téma típusa

        Returns:
            Komplett CSS stylesheet
        """
        css_parts = []

        # Widget típusok CSS generálása
        widget_types = [
            "container",  # QMainWindow, QWidget alapok
            "button",  # QPushButton és variánsai
            "input",  # QLineEdit, QComboBox, stb.
            "table",  # QTableWidget, QHeaderView
            "scrollbar",  # QScrollBar
            "splitter",  # QSplitter - JAVÍTOTT!
            "navigation",  # QToolBar, QToolButton
            "dialog",  # QDialog, QMessageBox
            "chart",  # Chart widget toggle-ök
        ]

        for widget_type in widget_types:
            try:
                widget_css = manager.generate_css_for_class(widget_type)
                if widget_css:
                    css_parts.append(f"/* {widget_type.upper()} WIDGETS */")
                    css_parts.append(widget_css)
                    css_parts.append("")  # Empty line separator
            except Exception as e:
                logger.warning(f"CSS generation failed for {widget_type}: {e}")

        return "\n".join(css_parts)

    @staticmethod
    def _get_legacy_stylesheet(theme_type: ThemeType) -> str:
        """Legacy CSS fallback ha ThemeManager nem elérhető."""
        if theme_type == ThemeType.DARK:
            return StyleSheets._LEGACY_DARK_THEME
        else:
            return StyleSheets._LEGACY_LIGHT_THEME

    @staticmethod
    def get_widget_stylesheet(
        widget_class: str, theme_type: Optional[ThemeType] = None
    ) -> str:
        """
        🎨 Widget-specifikus CSS lekérdezése ThemeManager-rel.

        Args:
            widget_class: Widget típus ("button", "input", "splitter", stb.)
            theme_type: Téma típusa, None esetén jelenlegi

        Returns:
            Widget CSS stylesheet
        """
        try:
            from ..theme_manager import get_theme_manager

            manager = get_theme_manager()

            # Téma beállítása ha megadva
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
        🎨 Téma alkalmazása egyetlen widget-re ThemeManager-rel.

        Args:
            widget: Qt widget instance
            widget_class: Widget típus
            theme_type: Téma típusa, None esetén jelenlegi
        """
        try:
            from ..theme_manager import get_theme_manager

            manager = get_theme_manager()

            # Widget regisztrálása és styling alkalmazása
            manager.register_widget(widget, widget_class)

            logger.debug(
                f"Theme applied to widget: {widget.__class__.__name__} as {widget_class}"
            )

        except Exception as e:
            logger.error(f"Widget theme application failed: {e}")

            # Fallback - widget-specifikus CSS lekérdezése és manuális alkalmazás
            css = StyleSheets.get_widget_stylesheet(widget_class, theme_type)
            if css:
                widget.setStyleSheet(css)

    # === BACKWARD COMPATIBILITY PROPERTIES ===

    @property
    def LIGHT_THEME(self) -> str:
        """🔄 Backward compatibility - dinamikus light theme."""
        return self.get_theme_stylesheet(ThemeType.LIGHT)

    @property
    def DARK_THEME(self) -> str:
        """🔄 Backward compatibility - dinamikus dark theme."""
        return self.get_theme_stylesheet(ThemeType.DARK)


def log_theme_change(from_theme: str, to_theme: str) -> None:
    """
    Téma váltás naplózása.

    Args:
        from_theme: Előző téma neve
        to_theme: Új téma neve
    """
    logger.info(f"THEME CHANGE: {from_theme} → {to_theme}")


def log_wind_gusts_event(value: float, location: str = "Unknown") -> None:
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés esemény naplózása.

    Args:
        value: Széllökés érték
        location: Helyszín
    """
    from .formatting import get_wind_gusts_category

    category = get_wind_gusts_category(value)
    if category:
        logger.info(
            f"WIND GUSTS: {value:.1f} km/h at {location} - {category['emoji']} {category['label']}"
        )
    else:
        logger.info(f"WIND GUSTS: {value:.1f} km/h at {location}")


__all__ = [
    "StyleSheets",
    "log_theme_change",
    "log_wind_gusts_event",
]
