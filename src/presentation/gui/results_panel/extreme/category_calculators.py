#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Category Calculators
🌡️ Kategória alapú rekord számítások (temperature/precipitation/wind)
"""

import logging
from typing import Dict, List, Tuple, Optional

from .extreme_records import ExtremeRecord

logger = logging.getLogger(__name__)


class CategoryCalculators:
    """
    🌡️ Kategória alapú rekord számítások

    Felelős:
    - Hőmérséklet rekordok számítása
    - Csapadék rekordok számítása
    - Szél rekordok számítása
    """

    def calculate_temperature_records(
        self,
        daily_data: Dict[str, List],
        dates: List[str]
    ) -> List[ExtremeRecord]:
        """Hőmérséklet rekordok számítása."""
        records = []

        try:
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])

            if temp_max_list and len(temp_max_list) == len(dates):
                clean_max = [(i, t) for i, t in enumerate(temp_max_list) if t is not None]
                if clean_max:
                    max_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb nap",
                        value=f"{max_temp:.1f}°C",
                        date=dates[max_idx],
                        raw_value=float(max_temp)
                    ))

            if temp_min_list and len(temp_min_list) == len(dates):
                clean_min = [(i, t) for i, t in enumerate(temp_min_list) if t is not None]
                if clean_min:
                    min_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb nap",
                        value=f"{min_temp:.1f}°C",
                        date=dates[min_idx],
                        raw_value=float(min_temp)
                    ))

            # Legnagyobb napi hőingás
            if temp_max_list and temp_min_list:
                daily_ranges = []
                for i in range(min(len(temp_max_list), len(temp_min_list))):
                    if temp_max_list[i] is not None and temp_min_list[i] is not None:
                        daily_range = temp_max_list[i] - temp_min_list[i]
                        daily_ranges.append((i, daily_range))

                if daily_ranges:
                    max_range_idx, max_range = max(daily_ranges, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="📊 Legnagyobb napi hőingás",
                        value=f"{max_range:.1f}°C",
                        date=dates[max_range_idx],
                        raw_value=float(max_range)
                    ))

        except Exception as e:
            logger.error(f"Hőmérséklet rekordok hiba: {e}")

        return records

    def calculate_precipitation_records(
        self,
        daily_data: Dict[str, List],
        dates: List[str]
    ) -> List[ExtremeRecord]:
        """Csapadék rekordok számítása."""
        records = []

        try:
            precip_list = daily_data.get('precipitation_sum', [])
            if precip_list and len(precip_list) == len(dates):
                clean_precip = [(i, p) for i, p in enumerate(precip_list) if p is not None]
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="💧 Legcsapadékosabb nap",
                        value=f"{max_precip:.1f}mm",
                        date=dates[max_precip_idx],
                        raw_value=float(max_precip)
                    ))

        except Exception as e:
            logger.error(f"Csapadék rekordok hiba: {e}")

        return records

    def calculate_wind_records(
        self,
        daily_data: Dict[str, List],
        dates: List[str]
    ) -> List[ExtremeRecord]:
        """Széllökés rekordok számítása."""
        records = []

        try:
            wind_data, wind_source = self._get_wind_data(daily_data)

            if wind_data and len(wind_data) == len(dates):
                clean_wind = [(i, w) for i, w in enumerate(wind_data) if w is not None]
                if clean_wind:
                    max_wind_idx, max_wind = max(clean_wind, key=lambda x: x[1])

                    from ..utils import WindGustsAnalyzer, WindGustsConstants
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(
                            max_wind, wind_source
                        )
                        category_info = WindGustsConstants.CATEGORIES.get(
                            category, 'ISMERETLEN'
                        )
                        records.append(ExtremeRecord(
                            category="🌪️ Széllökés",
                            record_type=f"🚨 Legerősebb ({category_info})",
                            value=f"{max_wind:.1f}km/h",
                            date=dates[max_wind_idx],
                            raw_value=float(max_wind)
                        ))
                    else:
                        records.append(ExtremeRecord(
                            category="💨 Szél",
                            record_type="🌪️ Legszelesebb nap",
                            value=f"{max_wind:.1f}km/h",
                            date=dates[max_wind_idx],
                            raw_value=float(max_wind)
                        ))

        except Exception as e:
            logger.error(f"Széllökés rekordok hiba: {e}")

        return records

    @staticmethod
    def _get_wind_data(daily_data: Dict[str, List]) -> Tuple[Optional[List], str]:
        """Széladatok prioritás alapú kiválasztása."""
        wind_gusts_max = daily_data.get('wind_gusts_max', [])
        windspeed_10m_max = daily_data.get('windspeed_10m_max', [])
        windspeed = daily_data.get('windspeed', [])

        if wind_gusts_max:
            return wind_gusts_max, "wind_gusts_max"
        elif windspeed_10m_max:
            return windspeed_10m_max, "windspeed_10m_max"
        elif windspeed:
            return windspeed, "windspeed"
        else:
            return None, "no_data"
