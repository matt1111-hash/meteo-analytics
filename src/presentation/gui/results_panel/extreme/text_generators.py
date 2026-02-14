#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Text Generators
📋 Szöveges rekord összefoglalók generálása
"""

import logging
from typing import Dict, List

from .extreme_records import RecordsTextSummary

logger = logging.getLogger(__name__)


class TextGenerators:
    """
    📋 Szöveges rekord összefoglalók generálása

    Felelős:
    - Hőmérséklet szöveges összefoglaló
    - Csapadék szöveges összefoglaló
    - Széllökés szöveges összefoglaló
    """

    def generate_summary(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> RecordsTextSummary:
        """
        📋 Szöveges rekord összefoglaló generálása.

        Args:
            daily_data: Daily adatok Dict[List] formátumban
            dates: Dátumok listája

        Returns:
            RecordsTextSummary: Strukturált szöveges összefoglaló
        """
        try:
            temp_text = self._generate_temperature_text(daily_data, dates)
            precip_text = self._generate_precipitation_text(daily_data, dates)
            wind_text = self._generate_wind_text(daily_data, dates)

            return RecordsTextSummary(
                temperature_text=temp_text,
                precipitation_text=precip_text,
                wind_text=wind_text,
            )

        except Exception as e:
            logger.error(f"Szöveges összefoglaló hiba: {e}")
            return RecordsTextSummary(
                temperature_text="🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n",
                precipitation_text="🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n",
                wind_text="🌪️ SZÉLLÖKÉS REKORDOK: Hiba a számítás során\n",
            )

    def _generate_temperature_text(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> str:
        """Hőmérséklet szöveges összefoglaló."""
        try:
            temp_max_list = daily_data.get("temperature_2m_max", [])
            temp_min_list = daily_data.get("temperature_2m_min", [])

            if (
                temp_max_list
                and temp_min_list
                and len(temp_max_list) == len(dates)
                and len(temp_min_list) == len(dates)
            ):
                clean_max = [
                    (i, t) for i, t in enumerate(temp_max_list) if t is not None
                ]
                clean_min = [
                    (i, t) for i, t in enumerate(temp_min_list) if t is not None
                ]

                if clean_max and clean_min:
                    max_temp_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    min_temp_idx, min_temp = min(clean_min, key=lambda x: x[1])

                    return f"""🌡️ HŐMÉRSÉKLET REKORDOK:
   🔥 Legmelegebb nap: {max_temp:.1f}°C ({dates[max_temp_idx]})
   🧊 Leghidegebb nap: {min_temp:.1f}°C ({dates[min_temp_idx]})
   📈 Hőingás: {max_temp - min_temp:.1f}°C

"""
            return "🌡️ HŐMÉRSÉKLET REKORDOK: Nincs megfelelő adat\n\n"
        except Exception as e:
            logger.error(f"Hőmérséklet szöveg hiba: {e}")
            return "🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n\n"

    def _generate_precipitation_text(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> str:
        """Csapadék szöveges összefoglaló."""
        try:
            precip_list = daily_data.get("precipitation_sum", [])

            if precip_list and len(precip_list) == len(dates):
                clean_precip = [
                    (i, p) for i, p in enumerate(precip_list) if p is not None
                ]

                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    dry_days = len(
                        [p for p in precip_list if p is not None and p <= 0.1]
                    )
                    total_precip = sum([p for p in precip_list if p is not None])

                    return f"""🌧️ CSAPADÉK REKORDOK:
   💧 Legtöbb csapadék: {max_precip:.1f}mm ({dates[max_precip_idx]})
   🏜️ Száraz napok: {dry_days} nap
   📊 Összes csapadék: {total_precip:.1f}mm

"""
            return "🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
        except Exception as e:
            logger.error(f"Csapadék szöveg hiba: {e}")
            return "🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n\n"

    def _generate_wind_text(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """Széllökés szöveges összefoglaló."""
        try:
            wind_data, wind_source = self._get_wind_data(daily_data)

            if wind_data and len(wind_data) == len(dates):
                clean_wind = [(i, w) for i, w in enumerate(wind_data) if w is not None]

                if clean_wind:
                    max_wind_idx, max_wind_value = max(clean_wind, key=lambda x: x[1])
                    valid_winds = [w for w in wind_data if w is not None]
                    avg_wind = sum(valid_winds) / len(valid_winds)

                    from ..utils import WindGustsAnalyzer, WindGustsConstants

                    if wind_source == "wind_gusts_max":
                        category = WindGustsAnalyzer.categorize_wind_gust(
                            max_wind_value, wind_source
                        )

                        text = f"""🌪️ SZÉLLÖKÉS REKORDOK:
   🚨 Legerősebb széllökés: {max_wind_value:.1f}km/h ({dates[max_wind_idx]})
"""

                        if category == "hurricane":
                            text += (
                                f"   ⚠️ KATEGÓRIA: "
                                f"{WindGustsConstants.CATEGORIES[category]} "
                                f"(>{WindGustsConstants.HURRICANE_THRESHOLD:.0f} km/h)\n"
                            )
                        elif category == "extreme":
                            text += (
                                f"   ⚠️ KATEGÓRIA: "
                                f"{WindGustsConstants.CATEGORIES[category]} "
                                f"(>{WindGustsConstants.EXTREME_THRESHOLD:.0f} km/h)\n"
                            )
                        elif category == "strong":
                            text += (
                                f"   ⚠️ KATEGÓRIA: "
                                f"{WindGustsConstants.CATEGORIES[category]} "
                                f"(>{WindGustsConstants.STRONG_THRESHOLD:.0f} km/h)\n"
                            )
                        else:
                            text += f"   ✅ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]}\n"
                    else:
                        text = f"""💨 SZÉL REKORDOK:
   🌪️ Legerősebb szél: {max_wind_value:.1f}km/h ({dates[max_wind_idx]})
"""

                    text += f"   📊 Átlagos szélsebesség: {avg_wind:.1f}km/h\n"
                    text += f"   📈 Adatforrás: {wind_source}\n\n"

                    return text

            return "🌪️ SZÉLLÖKÉS REKORDOK: Nincs szél adat\n\n"
        except Exception as e:
            logger.error(f"Széllökés szöveg hiba: {e}")
            return "🌪️ SZÉLLÖKÉS REKORDOK: Hiba a számítás során\n\n"

    @staticmethod
    def _get_wind_data(daily_data: Dict[str, List]) -> tuple[list | None, str]:
        """Széladatok prioritás alapú kiválasztása."""
        wind_gusts_max = daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])
        windspeed = daily_data.get("windspeed", [])

        if wind_gusts_max:
            return wind_gusts_max, "wind_gusts_max"
        elif windspeed_10m_max:
            return windspeed_10m_max, "windspeed_10m_max"
        elif windspeed:
            return windspeed, "windspeed"
        else:
            return None, "no_data"
