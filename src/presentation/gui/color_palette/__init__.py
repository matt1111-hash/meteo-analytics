#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette Module - RED THEME VERSION
🎨 KRITIKUS JAVÍTÁS: Piros (#C43939) Primary Téma hozzáadva - UNDORÍTÓ LILA ELTÁVOLÍTVA!

🎨 FŐBB FUNKCIÓK:
✅ Automatikus színvariáns generálás egyetlen base színből
✅ Semantic color mapping (primary, success, warning, error, info)
✅ HSL/HSV color space manipuláció
✅ WCAG accessibility compliance checking
✅ Color harmony generálás (complementary, triadic, analogous)
✅ Adaptive color schemes (light/dark theme optimalization)
✅ Color blindness simulation és optimization
✅ Export/import színpaletta JSON formátumban
✅ Real-time color preview generation
✅ Material Design color generator
✅ PIROS (#C43939) PRIMARY TÉMA - GYÖNYÖRŰ MEGJELENÍTÉS!

🚨 KRITIKUS JAVÍTÁS: "red" preset hozzáadva - primary: #C43939
"""

# Re-export types
# Re-export accessibility
from src.presentation.gui.color_palette.accessibility import (
    calculate_contrast_ratio,
    get_color_metrics,
    simulate_color_blindness,
    suggest_accessible_variants,
)

# Re-export core
from src.presentation.gui.color_palette.core import ColorPalette

# Re-export factory functions
from src.presentation.gui.color_palette.factory import (
    create_color_palette,
    create_material_palette,
    create_weather_palette,
)

# Re-export generators
from src.presentation.gui.color_palette.generators import (
    ColorGenerator,
    MaterialColorGenerator,
    StandardColorGenerator,
)

# Re-export harmony
from src.presentation.gui.color_palette.harmony import generate_harmony

# Re-export presets
from src.presentation.gui.color_palette.presets import (
    get_preset,
    get_semantic_presets,
    is_valid_preset,
)
from src.presentation.gui.color_palette.types import (
    ColorBlindnessType,
    ColorFormat,
    ColorHarmony,
    ColorMetrics,
    HSLColor,
)

# Re-export utility functions
from src.presentation.gui.color_palette.utils import (
    calculate_color_contrast,
    generate_color_variants,
    generate_weather_color_scheme,
    hex_to_hsl,
)

# Re-export weather
from src.presentation.gui.color_palette.weather import (
    generate_alert_gradient,
    generate_weather_palette,
)

__all__ = [
    # Types
    "ColorFormat",
    "ColorHarmony",
    "ColorBlindnessType",
    "ColorMetrics",
    "HSLColor",
    # Generators
    "ColorGenerator",
    "StandardColorGenerator",
    "MaterialColorGenerator",
    # Core
    "ColorPalette",
    # Presets
    "get_semantic_presets",
    "get_preset",
    "is_valid_preset",
    # Accessibility
    "calculate_contrast_ratio",
    "get_color_metrics",
    "suggest_accessible_variants",
    "simulate_color_blindness",
    # Harmony
    "generate_harmony",
    # Weather
    "generate_weather_palette",
    "generate_alert_gradient",
    # Factory
    "create_color_palette",
    "create_material_palette",
    "create_weather_palette",
    # Utils
    "hex_to_hsl",
    "calculate_color_contrast",
    "generate_color_variants",
    "generate_weather_color_scheme",
]
