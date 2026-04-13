#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Map Constants - Folium térkép konstansok és színskálák.

FÁJL: src/presentation/gui/map/map_constants.py
"""


# === Térkép alapértelmezett beállítások ===

HUNGARY_CENTER = {
    "lat": 47.1625,
    "lon": 19.5033,
    "zoom_start": 7,
    "min_zoom": 6,
    "max_zoom": 12,
}

# === Dinamikus színskála mapping ===

COLOR_SCALE_GRADIENTS: dict[str, dict[float, str]] = {
    "RdYlBu_r": {  # Hőmérséklet - Kék (hideg) → Piros (meleg)
        0.0: "#0000FF",  # Kék
        0.2: "#00BFFF",  # Világoskék
        0.4: "#87CEEB",  # Égkék
        0.6: "#FFFF00",  # Sárga
        0.8: "#FFA500",  # Narancs
        1.0: "#FF0000",  # Piros
    },
    "Blues": {  # Csapadék - Fehér → Sötétkék
        0.0: "#F0F8FF",  # Alice Blue (szinte fehér)
        0.2: "#E6F3FF",  # Nagyon világoskék
        0.4: "#B3D9FF",  # Világoskék
        0.6: "#4D94FF",  # Közepes kék
        0.8: "#0066CC",  # Sötétkék
        1.0: "#003366",  # Nagyon sötétkék
    },
    "Greens": {  # Szél - Világoszöld → Sötétzöld
        0.0: "#F0FFF0",  # Honeydew (szinte fehér)
        0.2: "#98FB98",  # Pale Green
        0.4: "#90EE90",  # Light Green
        0.6: "#32CD32",  # Lime Green
        0.8: "#228B22",  # Forest Green
        1.0: "#006400",  # Dark Green
    },
    "Oranges": {  # Széllökések - Világos narancs → Sötét narancs/piros
        0.0: "#FFF8DC",  # Cornsilk (krémszín)
        0.2: "#FFEFD5",  # Papaya Whip
        0.4: "#FFE4B5",  # Moccasin
        0.6: "#FFA500",  # Orange
        0.8: "#FF4500",  # Orange Red
        1.0: "#DC143C",  # Crimson
    },
}

# Overlay type → color scale mapping

OVERLAY_COLOR_MAPPING: dict[str, str] = {
    "temperature": "RdYlBu_r",
    "precipitation": "Blues",
    "wind_speed": "Greens",
    "wind_gusts": "Oranges",
}

# === Megye stílus konstansok ===

COUNTY_STYLE_DEFAULT = {
    "fillColor": "#4A90E2",
    "color": "#2E4057",
    "weight": 2,
    "fillOpacity": 0.4,
}

COUNTY_STYLE_SELECTED = {
    "fillColor": "#E74C3C",
    "color": "#C0392B",
    "weight": 3,
    "fillOpacity": 0.7,
    "dashArray": "5, 5",
}

COUNTY_STYLE_HIGHLIGHTED = {
    "fillColor": "#F39C12",
    "color": "#E67E22",
    "weight": 3,
    "fillOpacity": 0.6,
}

COUNTY_STYLE_HOVER = {
    "fillColor": "#E74C3C",
    "color": "#FFFFFF",
    "weight": 4,
    "fillOpacity": 0.8,
}

# === Beaufort skála színek ===

BEAUFORT_COLORS: dict[str, str] = {
    "calm": "#C0C0C0",  # Szélcsend - Szürke
    "light_air": "#00FF00",  # Enyhe szél - Zöld
    "light_breeze": "#FFFF00",  # Gyenge szél - Sárga
    "gentle_breeze": "#FFA500",  # Mérsékelt szél - Narancs
    "moderate_breeze": "#FF8000",  # Élénk szél - Narancssárga
    "fresh_breeze": "#FF4000",  # Erős szél - Vörös-narancs
    "strong_breeze": "#FF0000",  # Viharos szél - Piros
    "gale": "#800000",  # Orkán - Sötét piros
}

# === Csapadék színek ===

PRECIPITATION_COLORS: dict[str, str] = {
    "none": "#CCCCCC",  # Szürke - nincs csapadék
    "trace": "#E8F4FD",  # Nagyon világos kék
    "light": "#BFE6FF",  # Világos kék
    "moderate": "#80D0FF",  # Közepes kék
    "heavy": "#40AAFF",  # Erős kék
    "violent": "#0080FF",  # Sötét kék
    "extreme": "#0040AA",  # Nagyon sötét kék
}

BEAUFORT_COLOR_STEPS = (
    (6, "calm"),
    (12, "light_air"),
    (20, "light_breeze"),
    (29, "gentle_breeze"),
    (39, "moderate_breeze"),
    (50, "fresh_breeze"),
    (62, "strong_breeze"),
)

PRECIPITATION_COLOR_STEPS = (
    (0, "none"),
    (1, "trace"),
    (5, "light"),
    (10, "moderate"),
    (25, "heavy"),
    (50, "violent"),
)


def get_beaufort_color(kmh: float) -> str:
    """
    Szél szín meghatározása Beaufort skála alapján.

    Args:
        kmh: Szélsebesség km/h-ban

    Returns:
        Hex színkód
    """
    for threshold, color_key in BEAUFORT_COLOR_STEPS:
        if kmh < threshold:
            return BEAUFORT_COLORS[color_key]
    return BEAUFORT_COLORS["gale"]


def get_precipitation_color(mm: float) -> str:
    """
    Csapadék szín meghatározása mennyiség alapján.

    Args:
        mm: Csapadék mennyiség milliméterben

    Returns:
        Hex színkód
    """
    if mm == 0:
        return PRECIPITATION_COLORS["none"]
    for threshold, color_key in PRECIPITATION_COLOR_STEPS[1:]:
        if mm < threshold:
            return PRECIPITATION_COLORS[color_key]
    return PRECIPITATION_COLORS["extreme"]


def get_gradient_for_overlay(overlay_type: str) -> dict[float, str]:
    """
    Gradient lekérdezése overlay típushoz.

    Args:
        overlay_type: Overlay típus (temperature, precipitation, wind_speed, wind_gusts)

    Returns:
        Gradient dictionary vagy default RdYlBu_r
    """
    color_scale = OVERLAY_COLOR_MAPPING.get(overlay_type, "RdYlBu_r")
    return COLOR_SCALE_GRADIENTS.get(color_scale, COLOR_SCALE_GRADIENTS["RdYlBu_r"])


# Export
__all__ = [
    "BEAUFORT_COLORS",
    "COLOR_SCALE_GRADIENTS",
    "COUNTY_STYLE_DEFAULT",
    "COUNTY_STYLE_HIGHLIGHTED",
    "COUNTY_STYLE_HOVER",
    "COUNTY_STYLE_SELECTED",
    "HUNGARY_CENTER",
    "OVERLAY_COLOR_MAPPING",
    "PRECIPITATION_COLORS",
    "get_beaufort_color",
    "get_gradient_for_overlay",
    "get_precipitation_color",
]
