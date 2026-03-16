# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for WindGustsAnalyzer."""

from __future__ import annotations

from .wind_analyzer_support import *


class WindGustsAnalyzerPart1Mixin:
    def __init__(self, constants_provider: Optional[Any] = None):
        """
        Initialize with dependency injection constants provider.

        Args:
            constants_provider: Optional constants provider for DI
        """
        # For dependency injection - can be extended later
        self.constants_provider = constants_provider

    def categorize_wind_gust(
        self, wind_speed: float, data_source: str = "wind_gusts_max"
    ) -> str:
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
            return "moderate"  # Default safe category

        try:
            if data_source in ["wind_gusts_max", "wind_gusts_10m_max"]:
                # ÉLETHŰ SZÉLLÖKÉS KÜSZÖBÖK (wind_gusts_max) - Dependency Injection
                hurricane_threshold = WindGustsConstants.HURRICANE_THRESHOLD
                extreme_threshold = WindGustsConstants.EXTREME_THRESHOLD
                strong_threshold = WindGustsConstants.STRONG_THRESHOLD
                moderate_threshold = WindGustsConstants.MODERATE_THRESHOLD

                if wind_speed >= hurricane_threshold:
                    return "hurricane"  # ≥120 km/h - Hurrikán (Beaufort 12)
                elif wind_speed >= extreme_threshold:
                    return "extreme"  # ≥100 km/h - Extrém vihar (Beaufort 10-11)
                elif wind_speed >= strong_threshold:
                    return "strong"  # ≥70 km/h - Erős vihar (Beaufort 8-9)
                elif wind_speed >= moderate_threshold:
                    return "strong"  # ≥50 km/h - Erős szél (Beaufort 7-8)
                else:
                    return "moderate"  # <50 km/h - Mérsékelt (Beaufort 1-6)

            else:
                # WINDSPEED_10M_MAX KÜSZÖBÖK (alacsonyabbak) - Dependency Injection
                # Use injected windspeed constants for clean architecture
                # Note: This would use the injected provider's constants in full DI
                high_threshold = 35.0  # Simplified for now

                if wind_speed >= high_threshold:
                    return "strong"
                else:
                    return "moderate"

        except Exception as e:
            logger.error(f"Wind gust categorization hiba: {e}")
            return "moderate"  # Safe fallback

    @staticmethod
    def get_windy_days_threshold(data_source: str) -> float:
        """
        Szeles napok küszöbének meghatározása adatforrás alapján.

        Args:
            data_source: Adatforrás típusa

        Returns:
            float: Küszöbérték km/h-ban
        """
        if data_source in ["wind_gusts_max", "wind_gusts_10m_max"]:
            return WindGustsConstants.WINDY_THRESHOLD_GUSTS  # 70.0 km/h
        else:
            return WindGustsConstants.WINDY_THRESHOLD_WINDSPEED  # 20.0 km/h

    @staticmethod
    def generate_wind_description(
        wind_speed: float, category: str, data_source: str
    ) -> str:
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
            category_label = WindGustsConstants.CATEGORIES.get(category, "ISMERETLEN")
            category_emoji = WindGustsConstants.CATEGORY_EMOJIS.get(category, "💨")

            if data_source in ["wind_gusts_max", "wind_gusts_10m_max"]:
                # Részletes széllökés leírás
                return f"{category_emoji} {category_label} ({wind_speed:.1f} km/h)"
            else:
                # Egyszerű szélsebesség leírás
                return f"💨 Szél: {wind_speed:.1f} km/h"

        except Exception as e:
            logger.error(f"Wind description generation hiba: {e}")
            return f"💨 {wind_speed:.1f} km/h"
