#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette - Color Management Module
Base color és color variant kezelő metódusok.
"""

from src.presentation.gui.color_palette.types import HSLColor


class ColorManagementMixin:
    """Color management metódusok ColorPalette osztályhoz."""

    def set_base_color(self, semantic_name: str, color: str | HSLColor) -> None:
        """
        Base szín beállítása semantic név alatt.

        Args:
            semantic_name: Semantic név ("primary", "success", stb.)
            color: Szín hex string vagy HSLColor formátumban
        """
        if isinstance(color, str):
            hsl_color = self._hex_to_hsl(color)
        else:
            hsl_color = color

        self._base_colors[semantic_name] = hsl_color

        # Variánsok automatikus generálása
        self._generate_variants_for_color(semantic_name)

        print(f"🎨 DEBUG: Base color set: {semantic_name} = {hsl_color.to_hex()}")

    def get_base_color(self, semantic_name: str) -> HSLColor | None:
        """Base szín lekérdezése semantic név alapján."""
        return self._base_colors.get(semantic_name)

    def set_multiple_base_colors(self, colors: dict[str, str | HSLColor]) -> None:
        """Több base szín egyszerre beállítása."""
        for semantic_name, color in colors.items():
            self.set_base_color(semantic_name, color)

    def get_color(self, semantic_name: str, variant: str = "base") -> str | None:
        """
        Szín lekérdezése semantic név és variáns alapján.

        Args:
            semantic_name: Semantic név ("primary", "success", stb.)
            variant: Variáns neve ("base", "light", "dark", "hover", stb.)

        Returns:
            Hex színkód vagy None ha nem található
        """
        if variant == "base":
            base_color = self._base_colors.get(semantic_name)
            return base_color.to_hex() if base_color else None

        variants = self._generated_variants.get(semantic_name, {})
        variant_color = variants.get(variant)
        return variant_color.to_hex() if variant_color else None

    def get_color_hsl(self, semantic_name: str, variant: str = "base") -> HSLColor | None:
        """Szín lekérdezése HSLColor formátumban."""
        if variant == "base":
            return self._base_colors.get(semantic_name)

        variants = self._generated_variants.get(semantic_name, {})
        return variants.get(variant)

    def get_all_variants(self, semantic_name: str) -> dict[str, str]:
        """
        Összes variáns lekérdezése egy semantic névhez.

        Args:
            semantic_name: Semantic név

        Returns:
            Variánsok {variant_name: hex_color} formátumban
        """
        result = {}

        # Base color
        base_color = self._base_colors.get(semantic_name)
        if base_color:
            result["base"] = base_color.to_hex()

        # Generated variants
        variants = self._generated_variants.get(semantic_name, {})
        for variant_name, variant_color in variants.items():
            result[variant_name] = variant_color.to_hex()

        return result
