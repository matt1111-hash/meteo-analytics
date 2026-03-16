#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
ThemeManager Accessibility - WCAG accessibility compliance features.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .core import ProfessionalThemeManager


class AccessibilityHelper:
    """Professional accessibility helper methods."""

    def __init__(self, manager: "ProfessionalThemeManager"):
        """
        Initialize accessibility helper.

        Args:
            manager: ThemeManager instance
        """
        self._manager = manager

    def get_info(self) -> Dict[str, Any]:
        """
        ♿ PROFESSIONAL ACCESSIBILITY - Get accessibility compliance info.

        Returns:
            Accessibility information for current theme
        """
        colors = self._manager.get_current_colors()

        accessibility_info = {
            "theme": self._manager.current_theme,
            "contrast_ratios": {},
            "wcag_compliance": {},
            "recommendations": [],
        }

        # Check contrast ratios
        if hasattr(self._manager.color_palette, "calculate_contrast_ratio"):
            try:
                primary_surface_contrast = (
                    self._manager.color_palette.calculate_contrast_ratio(
                        colors["primary"], colors["surface"]
                    )
                )
                text_surface_contrast = (
                    self._manager.color_palette.calculate_contrast_ratio(
                        colors["on_surface"], colors["surface"]
                    )
                )

                accessibility_info["contrast_ratios"] = {
                    "primary_on_surface": primary_surface_contrast,
                    "text_on_surface": text_surface_contrast,
                }

                # WCAG compliance
                accessibility_info["wcag_compliance"] = {
                    "primary_aa": primary_surface_contrast >= 4.5,
                    "primary_aaa": primary_surface_contrast >= 7.0,
                    "text_aa": text_surface_contrast >= 4.5,
                    "text_aaa": text_surface_contrast >= 7.0,
                }

                # Recommendations
                if primary_surface_contrast < 4.5:
                    accessibility_info["recommendations"].append(
                        "Primary color contrast below WCAG AA standard"
                    )
                if text_surface_contrast < 4.5:
                    accessibility_info["recommendations"].append(
                        "Text color contrast below WCAG AA standard"
                    )

            except Exception as e:
                accessibility_info["error"] = f"Accessibility check failed: {e}"

        return accessibility_info
