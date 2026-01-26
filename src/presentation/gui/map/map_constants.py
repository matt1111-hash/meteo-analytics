#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Map Constants - Folium térkép konstansok és színskálák.

FÁJL: src/presentation/gui/map/map_constants.py
"""

from typing import Dict

# === Térkép alapértelmezett beállítások ===

HUNGARY_CENTER = {
    "lat": 47.1625,
    "lon": 19.5033,
    "zoom_start": 7,
    "min_zoom": 6,
    "max_zoom": 12,
}

# === Dinamikus színskála mapping ===

COLOR_SCALE_GRADIENTS: Dict[str, Dict[float, str]] = {
    'RdYlBu_r': {  # Hőmérséklet - Kék (hideg) → Piros (meleg)
        0.0: '#0000FF',  # Kék
        0.2: '#00BFFF',  # Világoskék
        0.4: '#87CEEB',  # Égkék
        0.6: '#FFFF00',  # Sárga
        0.8: '#FFA500',  # Narancs
        1.0: '#FF0000'   # Piros
    },
    'Blues': {  # Csapadék - Fehér → Sötétkék
        0.0: '#F0F8FF',  # Alice Blue (szinte fehér)
        0.2: '#E6F3FF',  # Nagyon világoskék
        0.4: '#B3D9FF',  # Világoskék
        0.6: '#4D94FF',  # Közepes kék
        0.8: '#0066CC',  # Sötétkék
        1.0: '#003366'   # Nagyon sötétkék
    },
    'Greens': {  # Szél - Világoszöld → Sötétzöld
        0.0: '#F0FFF0',  # Honeydew (szinte fehér)
        0.2: '#98FB98',  # Pale Green
        0.4: '#90EE90',  # Light Green
        0.6: '#32CD32',  # Lime Green
        0.8: '#228B22',  # Forest Green
        1.0: '#006400'   # Dark Green
    },
    'Oranges': {  # Széllökések - Világos narancs → Sötét narancs/piros
        0.0: '#FFF8DC',  # Cornsilk (krémszín)
        0.2: '#FFEFD5',  # Papaya Whip
        0.4: '#FFE4B5',  # Moccasin
        0.6: '#FFA500',  # Orange
        0.8: '#FF4500',  # Orange Red
        1.0: '#DC143C'   # Crimson
    }
}

# Overlay type → color scale mapping

OVERLAY_COLOR_MAPPING: Dict[str, str] = {
    'temperature': 'RdYlBu_r',
    'precipitation': 'Blues',
    'wind_speed': 'Greens',
    'wind_gusts': 'Oranges'
}

# === Megye stílus konstansok ===

COUNTY_STYLE_DEFAULT = {
    'fillColor': '#4A90E2',
    'color': '#2E4057',
    'weight': 2,
    'fillOpacity': 0.4
}

COUNTY_STYLE_SELECTED = {
    'fillColor': '#E74C3C',
    'color': '#C0392B',
    'weight': 3,
    'fillOpacity': 0.7,
    'dashArray': '5, 5'
}

COUNTY_STYLE_HIGHLIGHTED = {
    'fillColor': '#F39C12',
    'color': '#E67E22',
    'weight': 3,
    'fillOpacity': 0.6
}

COUNTY_STYLE_HOVER = {
    'fillColor': '#E74C3C',
    'color': '#FFFFFF',
    'weight': 4,
    'fillOpacity': 0.8
}

# === Beaufort skála színek ===

BEAUFORT_COLORS: Dict[str, str] = {
    'calm': '#C0C0C0',      # Szélcsend - Szürke
    'light_air': '#00FF00',  # Enyhe szél - Zöld
    'light_breeze': '#FFFF00',  # Gyenge szél - Sárga
    'gentle_breeze': '#FFA500',  # Mérsékelt szél - Narancs
    'moderate_breeze': '#FF8000',  # Élénk szél - Narancssárga
    'fresh_breeze': '#FF4000',  # Erős szél - Vörös-narancs
    'strong_breeze': '#FF0000',  # Viharos szél - Piros
    'gale': '#800000'       # Orkán - Sötét piros
}

# === Csapadék színek ===

PRECIPITATION_COLORS: Dict[str, str] = {
    'none': '#CCCCCC',      # Szürke - nincs csapadék
    'trace': '#E8F4FD',     # Nagyon világos kék
    'light': '#BFE6FF',     # Világos kék
    'moderate': '#80D0FF',  # Közepes kék
    'heavy': '#40AAFF',     # Erős kék
    'violent': '#0080FF',   # Sötét kék
    'extreme': '#0040AA'    # Nagyon sötét kék
}


def get_beaufort_color(kmh: float) -> str:
    """
    Szél szín meghatározása Beaufort skála alapján.

    Args:
        kmh: Szélsebesség km/h-ban

    Returns:
        Hex színkód
    """
    if kmh < 6:
        return BEAUFORT_COLORS['calm']
    elif kmh < 12:
        return BEAUFORT_COLORS['light_air']
    elif kmh < 20:
        return BEAUFORT_COLORS['light_breeze']
    elif kmh < 29:
        return BEAUFORT_COLORS['gentle_breeze']
    elif kmh < 39:
        return BEAUFORT_COLORS['moderate_breeze']
    elif kmh < 50:
        return BEAUFORT_COLORS['fresh_breeze']
    elif kmh < 62:
        return BEAUFORT_COLORS['strong_breeze']
    else:
        return BEAUFORT_COLORS['gale']


def get_precipitation_color(mm: float) -> str:
    """
    Csapadék szín meghatározása mennyiség alapján.

    Args:
        mm: Csapadék mennyiség milliméterben

    Returns:
        Hex színkód
    """
    if mm == 0:
        return PRECIPITATION_COLORS['none']
    elif mm < 1:
        return PRECIPITATION_COLORS['trace']
    elif mm < 5:
        return PRECIPITATION_COLORS['light']
    elif mm < 10:
        return PRECIPITATION_COLORS['moderate']
    elif mm < 25:
        return PRECIPITATION_COLORS['heavy']
    elif mm < 50:
        return PRECIPITATION_COLORS['violent']
    else:
        return PRECIPITATION_COLORS['extreme']


def get_gradient_for_overlay(overlay_type: str) -> Dict[float, str]:
    """
    Gradient lekérdezése overlay típushoz.

    Args:
        overlay_type: Overlay típus (temperature, precipitation, wind_speed, wind_gusts)

    Returns:
        Gradient dictionary vagy default RdYlBu_r
    """
    color_scale = OVERLAY_COLOR_MAPPING.get(overlay_type, 'RdYlBu_r')
    return COLOR_SCALE_GRADIENTS.get(color_scale, COLOR_SCALE_GRADIENTS['RdYlBu_r'])


# Export
__all__ = [
    'HUNGARY_CENTER',
    'COLOR_SCALE_GRADIENTS',
    'OVERLAY_COLOR_MAPPING',
    'COUNTY_STYLE_DEFAULT',
    'COUNTY_STYLE_SELECTED',
    'COUNTY_STYLE_HIGHLIGHTED',
    'COUNTY_STYLE_HOVER',
    'BEAUFORT_COLORS',
    'PRECIPITATION_COLORS',
    'get_beaufort_color',
    'get_precipitation_color',
    'get_gradient_for_overlay',
]
