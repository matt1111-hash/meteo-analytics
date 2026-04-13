# mypy: ignore-errors
# ruff: noqa: F403,noqa: I001
"""Split definitions from theme_helpers.py."""

from __future__ import annotations

from .theme_helpers_support import *


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


LEGACY_LIGHT_THEME_CSS = """
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
LEGACY_DARK_THEME_CSS = """
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
