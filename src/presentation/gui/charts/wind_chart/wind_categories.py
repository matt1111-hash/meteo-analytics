#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wind Chart Categories - Hungarian meteorological wind categories.
🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: 43-61-90-119 km/h küszöbök
"""

from typing import Dict, Tuple


# 🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY - Szélkategóriák
HUNGARIAN_WIND_THRESHOLDS = {
    'strong_wind': 43,      # Erős szél
    'stormy_wind': 61,      # Viharos szél
    'severe_storm': 90,     # Erős vihar
    'hurricane': 119,       # Orkán
}


def get_wind_category(windspeed: float) -> Dict[str, str]:
    """
    Get Hungarian wind category for a given wind speed.

    Args:
        windspeed: Wind speed in km/h

    Returns:
        Dictionary with category info: icon, name, beaufort, description, effects, intensity
    """
    if windspeed >= 119:
        return {
            'icon': "🚨",
            'name': "ORKÁN",
            'beaufort': "12",
            'description': "Pusztító szélerő",
            'effects': "🏠 Épületek rongálódnak, fák kidőlnek",
            'intensity': "Rendkívül veszélyes",
            'color_key': 'hurricane'
        }
    elif windspeed >= 90:
        return {
            'icon': "⚠️",
            'name': "Erős vihar",
            'beaufort': "10-11",
            'description': "Heves viharos szél",
            'effects': "🌳 Nagy fák törnek, tetőcserepek repülnek",
            'intensity': "Nagyon veszélyes",
            'color_key': 'severe_storm'
        }
    elif windspeed >= 61:
        return {
            'icon': "🌪️",
            'name': "Viharos szél",
            'beaufort': "8-9",
            'description': "Viharos erősségű szél",
            'effects': "🚗 Járművezetés nehéz, ágak törnek",
            'intensity': "Veszélyes",
            'color_key': 'stormy'
        }
    elif windspeed >= 43:
        return {
            'icon': "🌬️",
            'name': "Erős szél",
            'beaufort': "6-7",
            'description': "Erős széljárás",
            'effects': "☂️ Esernyő nehezen használható",
            'intensity': "Figyelmeztető",
            'color_key': 'strong'
        }
    elif windspeed >= 28:
        return {
            'icon': "💨",
            'name': "Mérsékelt szél",
            'beaufort': "4-5",
            'description': "Élénk széljárás",
            'effects': "🍃 Por és papír felemelkedik",
            'intensity': "Mérsékelt",
            'color_key': 'moderate'
        }
    elif windspeed >= 12:
        return {
            'icon': "🌱",
            'name': "Gyenge szél",
            'beaufort': "2-3",
            'description': "Gyenge széljárás",
            'effects': "🌿 Levelek mozognak, zászlók lengnek",
            'intensity': "Kellemes",
            'color_key': 'moderate'
        }
    elif windspeed >= 1:
        return {
            'icon': "🍃",
            'name': "Szellő",
            'beaufort': "1",
            'description': "Alig érezhető szellő",
            'effects': "🌾 Füst iránya látható",
            'intensity': "Gyenge",
            'color_key': 'moderate'
        }
    else:
        return {
            'icon': "😴",
            'name': "Szélcsend",
            'beaufort': "0",
            'description': "Nincs légmozgás",
            'effects': "🕯️ Láng egyenesen ég",
            'intensity': "Nincs szél",
            'color_key': 'moderate'
        }


def get_wind_recommendations(windspeed: float) -> list:
    """
    Get safety recommendations for a given wind speed.

    Args:
        windspeed: Wind speed in km/h

    Returns:
        List of recommendation strings
    """
    if windspeed > 50:
        return [
            "🏠 Épületek beltéri tartózkodás ajánlott",
            "🚫 Kültéri tevékenység kerülendő"
        ]
    elif windspeed > 30:
        return [
            "🚗 Óvatos közlekedés szükséges",
            "🌳 Fákra figyeljen"
        ]
    elif windspeed > 15:
        return [
            "🥾 Kültéri sportokhoz alkalmas",
            "⛵ Vitorlázáshoz jó körülmények"
        ]
    elif windspeed > 5:
        return [
            "🚴 Kerékpározáshoz ideális",
            "🏃 Futáshoz kellemes"
        ]
    return []


def calculate_y_axis_max(max_wind: float) -> int:
    """
    Calculate optimal Y-axis maximum for wind chart.

    Args:
        max_wind: Maximum wind speed in the data

    Returns:
        Optimal Y-axis maximum value
    """
    if max_wind >= 119:
        return int(max_wind * 1.1)  # Orkán feletti értékekhez
    elif max_wind >= 90:
        return 130  # Orkán küszöbig
    elif max_wind >= 61:
        return 100  # Erős vihar küszöbig
    elif max_wind >= 43:
        return 75   # Viharos szél küszöbig
    else:
        return 55   # Erős szél küszöbig
