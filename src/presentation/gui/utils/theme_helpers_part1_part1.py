# ruff: noqa: F403, F405
# mypy: ignore-errors
"""Mixin part 1 for StyleSheets."""

from __future__ import annotations

from .theme_helpers_part1_support import *


class StyleSheetsPart1Mixin:  # noqa: D101
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
    def _generate_full_application_css(manager, theme_type: ThemeType) -> str:  # noqa: ARG004
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
    def get_widget_stylesheet(widget_class: str, theme_type: Optional[ThemeType] = None) -> str:
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

            logger.debug(f"Theme applied to widget: {widget.__class__.__name__} as {widget_class}")

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
