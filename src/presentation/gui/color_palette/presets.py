#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette Presets Module
Előre definiált semantic színkészletek.
"""

from typing import Dict

from src.presentation.gui.types import ThemeType


def get_semantic_presets(theme_type: ThemeType) -> Dict[str, Dict[str, str]]:
    """
    Összes elérhető semantic preset lekérdezése.

    Args:
        theme_type: Téma típusa (light/dark)

    Returns:
        Preset dictionary {preset_name: {semantic_name: hex_color}}
    """
    return {
        "default": {
            "primary": "#2563eb",  # Blue
            "success": "#10b981",  # Emerald
            "warning": "#f59e0b",  # Amber
            "error": "#dc2626",  # Red
            "info": "#6b7280",  # Gray
            "surface": "#ffffff" if theme_type == ThemeType.LIGHT else "#1f2937",
            "background": "#f9fafb" if theme_type == ThemeType.LIGHT else "#111827",
        },
        "material": {
            "primary": "#1976d2",  # Material Blue
            "success": "#388e3c",  # Material Green
            "warning": "#f57c00",  # Material Orange
            "error": "#d32f2f",  # Material Red
            "info": "#1976d2",  # Material Blue
            "surface": "#ffffff" if theme_type == ThemeType.LIGHT else "#121212",
            "background": "#fafafa" if theme_type == ThemeType.LIGHT else "#000000",
        },
        "bootstrap": {
            "primary": "#0d6efd",  # Bootstrap Blue
            "success": "#198754",  # Bootstrap Green
            "warning": "#ffc107",  # Bootstrap Yellow
            "error": "#dc3545",  # Bootstrap Red
            "info": "#0dcaf0",  # Bootstrap Cyan
            "surface": "#ffffff" if theme_type == ThemeType.LIGHT else "#212529",
            "background": "#f8f9fa" if theme_type == ThemeType.LIGHT else "#000000",
        },
        "weather": {
            "primary": "#0ea5e9",  # Sky Blue
            "success": "#22c55e",  # Green
            "warning": "#eab308",  # Yellow (sun)
            "error": "#ef4444",  # Red (alert)
            "info": "#6366f1",  # Indigo
            "surface": "#ffffff" if theme_type == ThemeType.LIGHT else "#1e293b",
            "background": "#f1f5f9" if theme_type == ThemeType.LIGHT else "#0f172a",
        },
        # 🎨 KRITIKUS JAVÍTÁS: Piros (#C43939) PRIMARY TÉMA
        "red": {
            "primary": "#C43939",  # Beautiful Red (user request) 🎨
            "success": "#22c55e",  # Green
            "warning": "#f59e0b",  # Amber/Orange
            "error": "#dc2626",  # Red (darker than primary)
            "info": "#6b7280",  # Gray
            "surface": "#ffffff" if theme_type == ThemeType.LIGHT else "#1f2937",
            "background": "#f9fafb" if theme_type == ThemeType.LIGHT else "#111827",
        },
    }


def get_preset(preset_name: str, theme_type: ThemeType) -> Dict[str, str]:
    """
    Egy preset lekérdezése név alapján.

    Args:
        preset_name: Preset neve ("default", "material", "bootstrap", "weather", "red")
        theme_type: Téma típusa (light/dark)

    Returns:
        Szín dictionary {semantic_name: hex_color} vagy üres dict ha nem található
    """
    presets = get_semantic_presets(theme_type)
    return presets.get(preset_name, {})


def is_valid_preset(preset_name: str, theme_type: ThemeType = ThemeType.LIGHT) -> bool:
    """
    Ellenőrzi, hogy egy preset név létezik-e.

    Args:
        preset_name: Preset neve
        theme_type: Téma típusa

    Returns:
        True ha a preset létezik, egyébként False
    """
    return preset_name in get_semantic_presets(theme_type)
