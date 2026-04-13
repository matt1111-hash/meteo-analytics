#!/usr/bin/env python3
# mypy: ignore-errors

"""
Global Weather Analyzer - GUI Types Module.

Shared type definitions for the GUI layer.
Extracted to break circular dependencies between utils, theme_manager, and color_palette.

This module has NO dependencies on other gui modules.
"""

from enum import Enum


class ThemeType(Enum):
    """Theme type enumeration for light/dark mode support."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    HIGH_CONTRAST = "high_contrast"


class ColorVariant(Enum):
    """Color variant enumeration for dynamic color handling."""

    BASE = "base"
    LIGHT = "light"
    DARK = "dark"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"
