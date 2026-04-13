# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for WindGustsAnalyzer."""

from __future__ import annotations

from .wind_analyzer_support import *


def _calculate_basic_stats(
    wind_data: List[float], clean_data: List[float], data_source: str
) -> Dict[str, Any]:
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


def _count_wind_categories(clean_data: List[float], data_source: str) -> Dict[str, int]:
    """Count category distribution for clean wind values."""
    return {
        category: sum(
            1
            for speed in clean_data
            if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) == category
        )
        for category in ["moderate", "strong", "extreme", "hurricane"]
    }


def _count_risk_days(clean_data: List[float], data_source: str) -> int:
    """Count strong-or-above wind events."""
    risk_categories = {"strong", "extreme", "hurricane"}
    return sum(
        1
        for speed in clean_data
        if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) in risk_categories
    )


def _build_max_wind_details(max_speed: float, data_source: str) -> Dict[str, Any]:
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


class WindGustsAnalyzerPart2Mixin:  # noqa: D101
    @staticmethod
    def get_wind_risk_level(
        wind_speed: float, data_source: str = "wind_gusts_max"
    ) -> Dict[str, Any]:
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
                "actions": [],
            }

        try:
            category = WindGustsAnalyzer.categorize_wind_gust(wind_speed, data_source)

            risk_levels = {
                "moderate": {
                    "level": "low",
                    "color": "#10b981",  # Zöld
                    "warning": "Alacsony kockázat",
                    "actions": ["Szabadtéri tevékenységek biztonságosak"],
                },
                "strong": {
                    "level": "medium",
                    "color": "#f59e0b",  # Sárga
                    "warning": "Közepes kockázat",
                    "actions": [
                        "Óvatosság szabadban",
                        "Vezetésnél figyeljen a széllökésekre",
                    ],
                },
                "extreme": {
                    "level": "high",
                    "color": "#dc2626",  # Piros
                    "warning": "Magas kockázat",
                    "actions": [
                        "Kerülje a szabadtéri tevékenységeket",
                        "Biztosítsa a laza tárgyak",
                        "Vezetést kerülje",
                    ],
                },
                "hurricane": {
                    "level": "critical",
                    "color": "#7c2d12",  # Sötét piros
                    "warning": "KRITIKUS KOCKÁZAT",
                    "actions": [
                        "MARADJON BENT!",
                        "Kerülje az ablakokat",
                        "Készüljön áramkimaradásra",
                        "Kövesse a hivatalos figyelmeztetéseket",
                    ],
                },
            }

            return risk_levels.get(category, risk_levels["moderate"])

        except Exception as e:
            logger.error(f"Wind risk level calculation hiba: {e}")
            return {
                "level": "unknown",
                "color": "#9ca3af",
                "warning": "Hiba a számítás során",
                "actions": [],
            }

    @staticmethod
    def analyze_wind_series(
        wind_data: List[float], data_source: str = "wind_gusts_max"
    ) -> Dict[str, Any]:
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
            clean_data = [x for x in wind_data if x is not None and x >= 0]
            if not clean_data:
                return {"error": "Nincs érvényes szél adat"}
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
            return {"error": f"Elemzési hiba: {e!s}"}
