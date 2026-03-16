#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Universal Weather Research Platform - Analytics Helpers Module.
Segédfüggvények és színskálák az analytics view számára.

🎨 METEOROLÓGIAI SZÍNSKÁLÁK:
✅ BEAUFORT-alapú 13 fokozat progresszív színátmenet
✅ Meteorológiai csapadék színskála (0mm = fehér)
✅ Konstans heatmap támogatás

🔧 SAFE HELPERS:
✅ None-safe matematikai műveletek
✅ Statisztikai számítások
"""

import logging
from typing import List, Optional, Union

import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)


# 🎨 METEOROLÓGIAI SZÍNSKÁLÁK - KONSTANS HEATMAP-EKHEZ (BEAUFORT FRISSÍTETT)
class MeteorologicalColorMaps:
    """🎨 Professzionális meteorológiai színskálák heatmap-ekhez - BEAUFORT VERZIÓ"""

    @staticmethod
    def get_precipitation_colormap():
        """🌧️ Csapadék színskála - 0mm = FEHÉR!"""
        precipitation_levels = [0, 1, 5, 10, 20, 30, 40, 50, 80, 100]
        precipitation_colors = [
            "#FFFFFF",  # 0 mm - FEHÉR (száraz nap!)
            "#E6F3FF",  # 1 mm - nagyon világoskék
            "#CCE7FF",  # 5 mm - világoskék
            "#99D6FF",  # 10 mm - kék
            "#66C2FF",  # 20 mm - sötétkék
            "#3399FF",  # 30 mm - erős kék
            "#0066CC",  # 40 mm - sötét kék
            "#004499",  # 50 mm - nagyon sötét kék
            "#002266",  # 80 mm - sötétbordó
            "#001133",  # 100+ mm - fekete-kék
        ]

        cmap = mcolors.ListedColormap(precipitation_colors)
        norm = mcolors.BoundaryNorm(precipitation_levels, len(precipitation_colors))
        return cmap, norm

    @staticmethod
    def get_wind_colormap():
        """
        💨 BEAUFORT-ALAPÚ Magyar meteorológiai szél színskála - 13 FOKOZAT!

        🌈 PROGRESSZÍV SZÍNÁTMENET:
        Fehér → Világoskék → Zöld → Sárga → Narancs → Piros → Bíbor → Ibolya

        🎯 HÁROM LOGIKUS ZÓNA:
        • Alapfok (0-5): Fehér → Kék → Zöld (nyugodt szelek)
        • Elsőfok (6-7): Sárga → Narancs (figyelmeztető)
        • Másodfok (8-12): Piros → Bíbor → Ibolya (veszély)

        📊 BEAUFORT STANDARD:
        • 13 fokozat (0-12)
        • Hivatalos km/h határok
        • Meteorológiai szakmai megfelelés
        """

        # 🎯 BEAUFORT SZINTŰ HATÁROK (km/h) - 13 FOKOZAT
        beaufort_levels = [
            0,  # 0: Szélcsend
            1,  # 1: Gyenge szellő
            6,  # 2: Enyhe szél
            11,  # 3: Gyenge szél
            19,  # 4: Mérsékelt szél
            29,  # 5: Élénk szél
            39,  # 6: Erős szél
            49,  # 7: Viharos szél
            60,  # 8: Élénk viharos szél
            72,  # 9: Heves vihar
            85,  # 10: Dühöngő vihar
            100,  # 11: Heves szélvész
            115,  # 12: Orkán
            150,  # 12+: Szuper orkán (colorbar határhoz)
        ]

        # 🌈 BEAUFORT PROGRESSZÍV SZÍNPALETTA - INTUITÍV ÁTMENET
        beaufort_colors = [
            # === ALAPFOK ZÓNA (0-5): NYUGODT SZÍNEK ===
            "#FFFFFF",  # 0: Szélcsend - Tiszta fehér
            "#F0F8FF",  # 1: Gyenge szellő - Alice blue (nagyon halvány kék)
            "#E6F3FF",  # 2: Enyhe szél - Világos égkék
            "#CCE7FF",  # 3: Gyenge szél - Világosabb kék
            "#90EE90",  # 4: Mérsékelt szél - Világos zöld (természet)
            "#32CD32",  # 5: Élénk szél - Lime zöld (aktív, de biztonságos)
            # === ELSŐFOK ZÓNA (6-7): FIGYELMEZTETŐ SZÍNEK ===
            "#FFD700",  # 6: Erős szél - Arany sárga (FIGYELEM!)
            "#FFA500",  # 7: Viharos szél - Narancs (FOKOZOTT FIGYELEM!)
            # === MÁSODFOK ZÓNA (8-12): VESZÉLY SZÍNEK ===
            "#FF6347",  # 8: Élénk viharos - Paradicsom piros (VESZÉLY!)
            "#FF4500",  # 9: Heves vihar - Narancs-piros (NAGY VESZÉLY!)
            "#DC143C",  # 10: Dühöngő vihar - Crimson piros (SZÉLSŐSÉGES!)
            "#8B008B",  # 11: Heves szélvész - Sötét magenta (KRITIKUS!)
            "#4B0082",  # 12: Orkán - Indigo ibolya (KATASZTROFÁLIS!)
        ]

        # 🎨 MATPLOTLIB COLORMAP OBJEKTUMOK
        cmap = mcolors.ListedColormap(beaufort_colors)
        norm = mcolors.BoundaryNorm(beaufort_levels, len(beaufort_colors))

        return cmap, norm


# 🔧 NONE-SAFE HELPER FÜGGVÉNYEK
def safe_max(data_list: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe maximum érték számítás"""
    if not data_list:
        return None
    clean_data = [x for x in data_list if x is not None]
    return max(clean_data) if clean_data else None


def safe_min(data_list: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe minimum érték számítás"""
    if not data_list:
        return None
    clean_data = [x for x in data_list if x is not None]
    return min(clean_data) if clean_data else None


def safe_avg(data_list: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe átlag számítás"""
    if not data_list:
        return None
    clean_data = [x for x in data_list if x is not None]
    return sum(clean_data) / len(clean_data) if clean_data else None


def safe_sum(data_list: List[Union[float, int, None]]) -> float:
    """None-safe összeg számítás"""
    if not data_list:
        return 0.0
    clean_data = [x for x in data_list if x is not None]
    return sum(clean_data) if clean_data else 0.0


def safe_count(data_list: List[Union[float, int, None]], condition_func) -> int:
    """None-safe feltételes számolás"""
    if not data_list:
        return 0
    clean_data = [x for x in data_list if x is not None]
    return sum(1 for x in clean_data if condition_func(x))


__all__ = [
    "MeteorologicalColorMaps",
    "safe_max",
    "safe_min",
    "safe_avg",
    "safe_sum",
    "safe_count",
]
