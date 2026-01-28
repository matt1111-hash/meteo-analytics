#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results Panel Utils - Wind Analyzer

🌪️ Széllökés elemzéséért felelős utility osztály

Képességek:
- Széllökés kategorizálása (Beaufort skála)
- Windy days számítás
- Kockázati szint meghatározás
- Idősoros elemzés

Fájl: src/presentation/gui/results_panel/utils/wind_analyzer.py
"""

import logging
from typing import Any, Dict, List, Optional

from .wind_constants import WindGustsConstants

logger = logging.getLogger(__name__)


class WindGustsAnalyzer:
    """
    🌪️ Széllökés elemzéséért felelős utility osztály - Dependency Injection Friendly
    🚀 SOLID: Single Responsibility Principle + Dependency Injection
    🌪️ METEOROLÓGIAI STANDARDOK: Beaufort skála alapú kategorizálás
    """

    def __init__(self, constants_provider: Optional[Any] = None):
        """
        Initialize with dependency injection constants provider.

        Args:
            constants_provider: Optional constants provider for DI
        """
        # For dependency injection - can be extended later
        self.constants_provider = constants_provider

    def categorize_wind_gust(self, wind_speed: float, data_source: str = 'wind_gusts_max') -> str:
        """
        Széllökés kategorizálása élethű értékek alapján - Dependency Injection Frissítve
        🌪️ METEOROLÓGIAI KALIBRÁLÁS: Beaufort skála szerinti kategóriák - DI Pattern

        Args:
            wind_speed: Szélsebesség km/h-ban
            data_source: Adatforrás típusa ('wind_gusts_max' vagy 'windspeed_10m_max')

        Returns:
            str: Kategória neve ('moderate', 'strong', 'extreme', 'hurricane')
        """
        if wind_speed is None or wind_speed < 0:
            return 'moderate'  # Default safe category

        try:
            if data_source in ['wind_gusts_max', 'wind_gusts_10m_max']:
                # ÉLETHŰ SZÉLLÖKÉS KÜSZÖBÖK (wind_gusts_max) - Dependency Injection
                hurricane_threshold = WindGustsConstants.HURRICANE_THRESHOLD
                extreme_threshold = WindGustsConstants.EXTREME_THRESHOLD
                strong_threshold = WindGustsConstants.STRONG_THRESHOLD
                moderate_threshold = WindGustsConstants.MODERATE_THRESHOLD

                if wind_speed >= hurricane_threshold:
                    return 'hurricane'    # ≥120 km/h - Hurrikán (Beaufort 12)
                elif wind_speed >= extreme_threshold:
                    return 'extreme'      # ≥100 km/h - Extrém vihar (Beaufort 10-11)
                elif wind_speed >= strong_threshold:
                    return 'strong'       # ≥70 km/h - Erős vihar (Beaufort 8-9)
                elif wind_speed >= moderate_threshold:
                    return 'strong'       # ≥50 km/h - Erős szél (Beaufort 7-8)
                else:
                    return 'moderate'     # <50 km/h - Mérsékelt (Beaufort 1-6)

            else:
                # WINDSPEED_10M_MAX KÜSZÖBÖK (alacsonyabbak) - Dependency Injection
                # Use injected windspeed constants for clean architecture
                # Note: This would use the injected provider's constants in full DI
                high_threshold = 35.0  # Simplified for now

                if wind_speed >= high_threshold:
                    return 'strong'
                else:
                    return 'moderate'

        except Exception as e:
            logger.error(f"Wind gust categorization hiba: {e}")
            return 'moderate'  # Safe fallback

    @staticmethod
    def get_windy_days_threshold(data_source: str) -> float:
        """
        Szeles napok küszöbének meghatározása adatforrás alapján.

        Args:
            data_source: Adatforrás típusa

        Returns:
            float: Küszöbérték km/h-ban
        """
        if data_source in ['wind_gusts_max', 'wind_gusts_10m_max']:
            return WindGustsConstants.WINDY_THRESHOLD_GUSTS  # 70.0 km/h
        else:
            return WindGustsConstants.WINDY_THRESHOLD_WINDSPEED  # 20.0 km/h

    @staticmethod
    def generate_wind_description(wind_speed: float, category: str, data_source: str) -> str:
        """
        Széllökés leírásának generálása.

        Args:
            wind_speed: Szélsebesség km/h-ban
            category: Kategória ('moderate', 'strong', 'extreme', 'hurricane')
            data_source: Adatforrás típusa

        Returns:
            str: Leírás szöveg emoji-val és értékkel
        """
        if wind_speed is None:
            return "❓ Nincs adat"

        try:
            # Kategória címke és emoji lekérdezése
            category_label = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
            category_emoji = WindGustsConstants.CATEGORY_EMOJIS.get(category, '💨')

            if data_source in ['wind_gusts_max', 'wind_gusts_10m_max']:
                # Részletes széllökés leírás
                return f"{category_emoji} {category_label} ({wind_speed:.1f} km/h)"
            else:
                # Egyszerű szélsebesség leírás
                return f"💨 Szél: {wind_speed:.1f} km/h"

        except Exception as e:
            logger.error(f"Wind description generation hiba: {e}")
            return f"💨 {wind_speed:.1f} km/h"

    @staticmethod
    def get_wind_risk_level(wind_speed: float, data_source: str = 'wind_gusts_max') -> Dict[str, Any]:
        """
        Széllökés kockázati szint meghatározása.

        Args:
            wind_speed: Szélsebesség km/h-ban
            data_source: Adatforrás típusa

        Returns:
            Dict: Kockázati információk (level, color, warning, actions)
        """
        if wind_speed is None:
            return {
                "level": "unknown",
                "color": "#9ca3af",
                "warning": "Nincs adat",
                "actions": []
            }

        try:
            category = WindGustsAnalyzer.categorize_wind_gust(wind_speed, data_source)

            risk_levels = {
                'moderate': {
                    "level": "low",
                    "color": "#10b981",  # Zöld
                    "warning": "Alacsony kockázat",
                    "actions": ["Szabadtéri tevékenységek biztonságosak"]
                },
                'strong': {
                    "level": "medium",
                    "color": "#f59e0b",  # Sárga
                    "warning": "Közepes kockázat",
                    "actions": [
                        "Óvatosság szabadban",
                        "Vezetésnél figyeljen a széllökésekre"
                    ]
                },
                'extreme': {
                    "level": "high",
                    "color": "#dc2626",  # Piros
                    "warning": "Magas kockázat",
                    "actions": [
                        "Kerülje a szabadtéri tevékenységeket",
                        "Biztosítsa a laza tárgyak",
                        "Vezetést kerülje"
                    ]
                },
                'hurricane': {
                    "level": "critical",
                    "color": "#7c2d12",  # Sötét piros
                    "warning": "KRITIKUS KOCKÁZAT",
                    "actions": [
                        "MARADJON BENT!",
                        "Kerülje az ablakokat",
                        "Készüljön áramkimaradásra",
                        "Kövesse a hivatalos figyelmeztetéseket"
                    ]
                }
            }

            return risk_levels.get(category, risk_levels['moderate'])

        except Exception as e:
            logger.error(f"Wind risk level calculation hiba: {e}")
            return {
                "level": "unknown",
                "color": "#9ca3af",
                "warning": "Hiba a számítás során",
                "actions": []
            }

    @staticmethod
    def analyze_wind_series(wind_data: List[float], data_source: str = 'wind_gusts_max') -> Dict[str, Any]:
        """
        Széllökés idősor elemzése.

        Args:
            wind_data: Széllökés értékek listája
            data_source: Adatforrás típusa

        Returns:
            Dict: Részletes elemzési eredmények
        """
        if not wind_data:
            return {"error": "Nincs szél adat"}

        try:
            # Tiszta adatok (None és negatív értékek eltávolítása)
            clean_data = [x for x in wind_data if x is not None and x >= 0]

            if not clean_data:
                return {"error": "Nincs érvényes szél adat"}

            # Alapstatisztikák
            import statistics

            analysis = {
                "data_source": data_source,
                "total_days": len(wind_data),
                "valid_days": len(clean_data),
                "missing_days": len(wind_data) - len(clean_data),

                # Statisztikák
                "min_speed": min(clean_data),
                "max_speed": max(clean_data),
                "avg_speed": statistics.mean(clean_data),
                "median_speed": statistics.median(clean_data),
                "std_dev": statistics.stdev(clean_data) if len(clean_data) > 1 else 0,

                # Kategória elemzés
                "categories": {},
                "windy_days": 0,
                "risk_days": 0
            }

            # Kategóriánkénti eloszlás
            for category in ['moderate', 'strong', 'extreme', 'hurricane']:
                count = len([
                    speed for speed in clean_data
                    if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) == category
                ])
                analysis["categories"][category] = count

            # Szeles napok száma
            threshold = WindGustsAnalyzer.get_windy_days_threshold(data_source)
            analysis["windy_days"] = len([x for x in clean_data if x > threshold])

            # Magas kockázatú napok (strong+)
            analysis["risk_days"] = len([
                speed for speed in clean_data
                if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) in ['strong', 'extreme', 'hurricane']
            ])

            # Maximum széllökés részletes adatai
            max_speed = max(clean_data)
            max_category = WindGustsAnalyzer.categorize_wind_gust(max_speed, data_source)
            max_risk = WindGustsAnalyzer.get_wind_risk_level(max_speed, data_source)

            analysis["max_wind_details"] = {
                "speed": max_speed,
                "category": max_category,
                "risk_level": max_risk["level"],
                "description": WindGustsAnalyzer.generate_wind_description(max_speed, max_category, data_source)
            }

            logger.debug(f"Wind series analysis completed: {len(clean_data)} days analyzed")
            return analysis

        except Exception as e:
            logger.error(f"Wind series analysis hiba: {e}")
            return {"error": f"Elemzési hiba: {str(e)}"}
