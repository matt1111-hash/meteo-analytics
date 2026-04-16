# mypy: ignore-errors
"""Results Panel Utils - Wind Analyzer - Szellokes elemzesis ert felelos utility osztaly."""

from __future__ import annotations

import logging
from typing import Any

from .wind_constants import WindGustsConstants

logger = logging.getLogger(__name__)


def _calculate_basic_stats(
    wind_data: list[float], clean_data: list[float], data_source: str
) -> dict[str, Any]:
    """Build base analysis statistics for a wind series."""
    import statistics  # noqa: PLC0415

    return {
        "data_source": data_source,
        "total_days": len(wind_data),
        "valid_days": len(clean_data),
        "missing_days": len(wind_data) - len(clean_data),
        "min_speed": min(clean_data),
        "max_speed": max(clean_data),
        "avg_speed": statistics.mean(clean_data),
        "median_speed": statistics.median(clean_data),
        "std_dev": statistics.stdev(clean_data) if len(clean_data) > 1 else 0,
        "categories": {},
        "windy_days": 0,
        "risk_days": 0,
    }


def _count_wind_categories(clean_data: list[float], data_source: str) -> dict[str, int]:
    """Count category distribution for clean wind values."""
    return {
        category: sum(
            1
            for speed in clean_data
            if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) == category
        )
        for category in ["moderate", "strong", "extreme", "hurricane"]
    }


def _count_risk_days(clean_data: list[float], data_source: str) -> int:
    """Count strong-or-above wind events."""
    risk_categories = {"strong", "extreme", "hurricane"}
    return sum(
        1
        for speed in clean_data
        if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) in risk_categories
    )


def _build_max_wind_details(max_speed: float, data_source: str) -> dict[str, Any]:
    """Build descriptive metadata for the maximum wind value."""
    max_category = WindGustsAnalyzer.categorize_wind_gust(max_speed, data_source)
    max_risk = WindGustsAnalyzer.get_wind_risk_level(max_speed, data_source)
    return {
        "speed": max_speed,
        "category": max_category,
        "risk_level": max_risk["level"],
        "description": WindGustsAnalyzer.generate_wind_description(
            max_speed, max_category, data_source
        ),
    }


class WindGustsAnalyzer:
    """
    Szellokes elemzesis ert felelos utility osztaly - Dependency Injection Friendly
    SOLID: Single Responsibility Principle + Dependency Injection
    METEOROLOGIAI STANDARDOK: Beaufort skala alapu kategorizalas
    """

    def __init__(self, constants_provider: Any | None = None):
        """
        Initialize with dependency injection constants provider.

        Args:
            constants_provider: Optional constants provider for DI
        """
        # For dependency injection - can be extended later
        self.constants_provider = constants_provider

    def categorize_wind_gust(  # noqa: PLR0911
        self, wind_speed: float, data_source: str = "wind_gusts_max"
    ) -> str:
        """
        Szellokes kategorizalasa elethu ertekek alapjan - Dependency Injection Frissitve
        METEOROLOGIAI KALIBRACIO: Beaufort skala szerinti kategoriak - DI Pattern

        Args:
            wind_speed: Szelsebesseg km/h-ban
            data_source: Adatforras tipusa ('wind_gusts_max' vagy 'windspeed_10m_max')

        Returns:
            str: Kategoria neve ('moderate', 'strong', 'extreme', 'hurricane')
        """
        if wind_speed is None or wind_speed < 0:
            return "moderate"  # Default safe category

        try:
            if data_source in ["wind_gusts_max", "wind_gusts_10m_max"]:
                # ELETHU SZELLOKES KUSZOBOK (wind_gusts_max) - Dependency Injection
                hurricane_threshold = WindGustsConstants.HURRICANE_THRESHOLD
                extreme_threshold = WindGustsConstants.EXTREME_THRESHOLD
                strong_threshold = WindGustsConstants.STRONG_THRESHOLD
                moderate_threshold = WindGustsConstants.MODERATE_THRESHOLD

                if wind_speed >= hurricane_threshold:
                    return "hurricane"  # >=120 km/h - Hurrikan (Beaufort 12)
                elif wind_speed >= extreme_threshold:
                    return "extreme"  # >=100 km/h - Extrem vihar (Beaufort 10-11)
                elif wind_speed >= strong_threshold:
                    return "strong"  # >=70 km/h - Eros vihar (Beaufort 8-9)
                elif wind_speed >= moderate_threshold:
                    return "strong"  # >=50 km/h - Eros szel (Beaufort 7-8)
                else:
                    return "moderate"  # <50 km/h - Mersekelt (Beaufort 1-6)

            else:
                # WINDSPEED_10M_MAX KUSZOBOK (alacsonyabbak) - Dependency Injection
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
        Szeles napok kuszobenek meghatarozasa adatforras alapjan.

        Args:
            data_source: Adatforras tipusa

        Returns:
            float: Kuszobertek km/h-ban
        """
        if data_source in ["wind_gusts_max", "wind_gusts_10m_max"]:
            return WindGustsConstants.WINDY_THRESHOLD_GUSTS  # 70.0 km/h
        else:
            return WindGustsConstants.WINDY_THRESHOLD_WINDSPEED  # 20.0 km/h

    @staticmethod
    def generate_wind_description(wind_speed: float, category: str, data_source: str) -> str:
        """
        Szellokes leirasának generalasa.

        Args:
            wind_speed: Szelsebesseg km/h-ban
            category: Kategoria ('moderate', 'strong', 'extreme', 'hurricane')
            data_source: Adatforras tipusa

        Returns:
            str: Leiras szoveg emoji-val es ertekkel
        """
        if wind_speed is None:
            return "Nincs adat"

        try:
            # Kategoria cimke es emoji lekerdezese
            category_label = WindGustsConstants.CATEGORIES.get(category, "ISMERETLEN")
            category_emoji = WindGustsConstants.CATEGORY_EMOJIS.get(category, "Szel")

            if data_source in ["wind_gusts_max", "wind_gusts_10m_max"]:
                # Reszletes szellokes leiras
                return f"{category_emoji} {category_label} ({wind_speed:.1f} km/h)"
            else:
                # Egyszeru szelsebesseg leiras
                return f"Szel: {wind_speed:.1f} km/h"

        except Exception as e:
            logger.error(f"Wind description generation hiba: {e}")
            return f"{wind_speed:.1f} km/h"

    @staticmethod
    def get_wind_risk_level(
        wind_speed: float, data_source: str = "wind_gusts_max"
    ) -> dict[str, Any]:
        """
        Szellokes kockazati szint meghatarozasa.

        Args:
            wind_speed: Szelsebesseg km/h-ban
            data_source: Adatforras tipusa

        Returns:
            Dict: Kockazati informaciok (level, color, warning, actions)
        """
        if wind_speed is None:
            return {
                "level": "unknown",
                "color": "#9ca3af",
                "warning": "Nincs adat",
                "actions": [],
            }

        try:
            category = WindGustsAnalyzer.categorize_wind_gust(wind_speed, data_source)

            risk_levels = {
                "moderate": {
                    "level": "low",
                    "color": "#10b981",  # Zold
                    "warning": "Alacsony kockazat",
                    "actions": ["Szabalteri tevekenysegek biztonsagosak"],
                },
                "strong": {
                    "level": "medium",
                    "color": "#f59e0b",  # Sarga
                    "warning": "Kozepes kockazat",
                    "actions": [
                        "Ovatosseg szabadban",
                        "Vezetesnel figyeljen a szellokesekre",
                    ],
                },
                "extreme": {
                    "level": "high",
                    "color": "#dc2626",  # Piros
                    "warning": "Magas kockazat",
                    "actions": [
                        "Kerulje a szabalteri tevekenysegeket",
                        "Biztositsea a laza targyak",
                        "Vezetest kerulje",
                    ],
                },
                "hurricane": {
                    "level": "critical",
                    "color": "#7c2d12",  # Sotet piros
                    "warning": "KRITIKUS KOCKAZAT",
                    "actions": [
                        "MARADJON BENT!",
                        "Kerulje az ablakokat",
                        "Keszuljon aramkimaradasra",
                        "Kovesse a hivatalos figyelmezteteseket",
                    ],
                },
            }

            return risk_levels.get(category, risk_levels["moderate"])

        except Exception as e:
            logger.error(f"Wind risk level calculation hiba: {e}")
            return {
                "level": "unknown",
                "color": "#9ca3af",
                "warning": "Hiba a szamitas soran",
                "actions": [],
            }

    @staticmethod
    def analyze_wind_series(
        wind_data: list[float], data_source: str = "wind_gusts_max"
    ) -> dict[str, Any]:
        """
        Szellokes idosor elemzese.

        Args:
            wind_data: Szellokes ertekek listaja
            data_source: Adatforras tipusa

        Returns:
            Dict: Reszletes elemzesi eredmenyek
        """
        if not wind_data:
            return {"error": "Nincs szel adat"}

        try:
            clean_data = [x for x in wind_data if x is not None and x >= 0]
            if not clean_data:
                return {"error": "Nincs ervenyes szel adat"}
            analysis = _calculate_basic_stats(wind_data, clean_data, data_source)
            analysis["categories"] = _count_wind_categories(clean_data, data_source)
            threshold = WindGustsAnalyzer.get_windy_days_threshold(data_source)
            analysis["windy_days"] = sum(1 for speed in clean_data if speed > threshold)
            analysis["risk_days"] = _count_risk_days(clean_data, data_source)
            max_speed = max(clean_data)
            analysis["max_wind_details"] = _build_max_wind_details(max_speed, data_source)
            logger.debug(f"Wind series analysis completed: {len(clean_data)} days analyzed")
            return analysis

        except Exception as e:
            logger.error(f"Wind series analysis hiba: {e}")
            return {"error": f"Elemzesi hiba: {e!s}"}
