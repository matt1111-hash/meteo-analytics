#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette Accessibility Module
WCAG accessibility compliance checking és color blindness simulation.
"""

from typing import Dict, Optional, Union

from src.presentation.gui.color_palette.types import (
    ColorBlindnessType,
    ColorMetrics,
    HSLColor,
)


def calculate_contrast_ratio(
    color1: Union[str, HSLColor], color2: Union[str, HSLColor], hex_to_hsl_func
) -> float:
    """
    WCAG kontraszt arány számítása két szín között.

    Args:
        color1: Első szín
        color2: Második szín
        hex_to_hsl_func: Hex → HSLColor konvertáló függvény

    Returns:
        Kontraszt arány (1.0-21.0)
    """

    def get_luminance(color: Union[str, HSLColor]) -> float:
        if isinstance(color, str):
            hsl = hex_to_hsl_func(color)
        else:
            hsl = color

        r, g, b = hsl.to_rgb()
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        # Gamma correction
        def gamma_correct(c):
            return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)

        r, g, b = map(gamma_correct, [r, g, b])
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    return (lighter + 0.05) / (darker + 0.05)


def get_color_metrics(color: HSLColor, calculate_contrast_func) -> ColorMetrics:
    """
    Szín accessibility metrikáinak lekérdezése.

    Args:
        color: HSLColor objektum
        calculate_contrast_func: Kontraszt számító függvény

    Returns:
        ColorMetrics objektum
    """
    # Luminance számítása
    r, g, b = color.to_rgb()
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Kontraszt arányok
    white_contrast = calculate_contrast_func(color, "#ffffff")
    black_contrast = calculate_contrast_func(color, "#000000")

    # WCAG compliance
    wcag_aa = white_contrast >= 4.5 or black_contrast >= 4.5
    wcag_aaa = white_contrast >= 7.0 or black_contrast >= 7.0

    return ColorMetrics(
        luminance=luminance,
        contrast_ratio=max(white_contrast, black_contrast),
        wcag_aa_compliant=wcag_aa,
        wcag_aaa_compliant=wcag_aaa,
        readable_on_white=white_contrast >= 4.5,
        readable_on_black=black_contrast >= 4.5,
    )


def suggest_accessible_variants(
    base_color: HSLColor,
    target_background: str,
    calculate_contrast_func,
    hex_to_hsl_func,
) -> Dict[str, str]:
    """
    Accessible variánsok javaslása adott háttérszínhez.

    Args:
        base_color: Base szín HSLColor formátumban
        target_background: Cél háttérszín hex formátumban
        calculate_contrast_func: Kontraszt számító függvény
        hex_to_hsl_func: Hex → HSLColor konvertáló függvény

    Returns:
        Javasolt variánsok {variant_name: hex_color}
    """
    suggestions = {}
    target_hsl = hex_to_hsl_func(target_background)

    # Lightness adjustment for accessibility
    if target_hsl.lightness > 50:  # Light background
        # Darker text colors needed
        for lightness in [40, 30, 20, 10]:
            variant_color = HSLColor(base_color.hue, base_color.saturation, lightness)
            contrast = calculate_contrast_func(variant_color, target_hsl)
            if contrast >= 4.5:
                suggestions[f"accessible_dark_{lightness}"] = variant_color.to_hex()
                break
    else:  # Dark background
        # Lighter text colors needed
        for lightness in [60, 70, 80, 90]:
            variant_color = HSLColor(base_color.hue, base_color.saturation, lightness)
            contrast = calculate_contrast_func(variant_color, target_hsl)
            if contrast >= 4.5:
                suggestions[f"accessible_light_{lightness}"] = variant_color.to_hex()
                break

    return suggestions


def simulate_color_blindness(
    color: HSLColor, blindness_type: ColorBlindnessType
) -> Optional[str]:
    """
    Színvakság szimuláció adott színre.

    Args:
        color: HSLColor objektum
        blindness_type: Színvakság típusa

    Returns:
        Szimulált szín hex formátumban
    """
    r, g, b = color.to_rgb()

    # Simplified color blindness simulation matrices
    if blindness_type == ColorBlindnessType.PROTANOPIA:
        # Red-blind simulation
        new_r = 0.567 * r + 0.433 * g
        new_g = 0.558 * r + 0.442 * g
        new_b = 0.242 * g + 0.758 * b
    elif blindness_type == ColorBlindnessType.DEUTERANOPIA:
        # Green-blind simulation
        new_r = 0.625 * r + 0.375 * g
        new_g = 0.700 * r + 0.300 * g
        new_b = 0.300 * g + 0.700 * b
    elif blindness_type == ColorBlindnessType.TRITANOPIA:
        # Blue-blind simulation
        new_r = 0.950 * r + 0.050 * g
        new_g = 0.433 * g + 0.567 * b
        new_b = 0.475 * g + 0.525 * b
    elif blindness_type == ColorBlindnessType.ACHROMATOPSIA:
        # Complete color blindness (grayscale)
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        new_r = new_g = new_b = gray
    else:
        return color.to_hex()

    # Ensure values are in valid range
    new_r = max(0, min(255, int(new_r)))
    new_g = max(0, min(255, int(new_g)))
    new_b = max(0, min(255, int(new_b)))

    return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
