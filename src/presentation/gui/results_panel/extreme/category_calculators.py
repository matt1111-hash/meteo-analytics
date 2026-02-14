#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Category Calculators
🌡️ Kategória alapú rekord számítások (temperature/precipitation/wind)
"""

import logging
from typing import Dict, List, Optional, Tuple

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
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Hőmérséklet rekordok számítása."""
        records = []

        try:
            temp_max_list = daily_data.get("temperature_2m_max", [])
            temp_min_list = daily_data.get("temperature_2m_min", [])

            if temp_max_list and len(temp_max_list) == len(dates):
                clean_max = [
                    (i, t) for i, t in enumerate(temp_max_list) if t is not None
                ]
                if clean_max:
                    max_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="🌡️ Hőmérséklet",
                            record_type="🔥 Legmelegebb nap",
                            value=f"{max_temp:.1f}°C",
                            date=dates[max_idx],
                            raw_value=float(max_temp),
                        )
                    )

            if temp_min_list and len(temp_min_list) == len(dates):
                clean_min = [
                    (i, t) for i, t in enumerate(temp_min_list) if t is not None
                ]
                if clean_min:
                    min_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="🌡️ Hőmérséklet",
                            record_type="🧊 Leghidegebb nap",
                            value=f"{min_temp:.1f}°C",
                            date=dates[min_idx],
                            raw_value=float(min_temp),
                        )
                    )

            # Legnagyobb napi hőingás
            if temp_max_list and temp_min_list:
                daily_ranges = []
                for i in range(min(len(temp_max_list), len(temp_min_list))):
                    if temp_max_list[i] is not None and temp_min_list[i] is not None:
                        daily_range = temp_max_list[i] - temp_min_list[i]
                        daily_ranges.append((i, daily_range))

                if daily_ranges:
                    max_range_idx, max_range = max(daily_ranges, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="🌡️ Hőmérséklet",
                            record_type="📊 Legnagyobb napi hőingás",
                            value=f"{max_range:.1f}°C",
                            date=dates[max_range_idx],
                            raw_value=float(max_range),
                        )
                    )

        except Exception as e:
            logger.error(f"Hőmérséklet rekordok hiba: {e}")

        return records

    def calculate_precipitation_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Csapadék rekordok számítása."""
        records = []

        try:
            precip_list = daily_data.get("precipitation_sum", [])
            if precip_list and len(precip_list) == len(dates):
                clean_precip = [
                    (i, p) for i, p in enumerate(precip_list) if p is not None
                ]
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="🌧️ Csapadék",
                            record_type="💧 Legcsapadékosabb nap",
                            value=f"{max_precip:.1f}mm",
                            date=dates[max_precip_idx],
                            raw_value=float(max_precip),
                        )
                    )

        except Exception as e:
            logger.error(f"Csapadék rekordok hiba: {e}")

        return records

    def calculate_wind_records(
        self, daily_data: Dict[str, List], dates: List[str]
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

                    if wind_source == "wind_gusts_max":
                        analyzer = WindGustsAnalyzer()
                        category = analyzer.categorize_wind_gust(max_wind, wind_source)
                        category_info = WindGustsConstants.CATEGORIES.get(
                            category, "ISMERETLEN"
                        )
                        records.append(
                            ExtremeRecord(
                                category="🌪️ Széllökés",
                                record_type=f"🚨 Legerősebb ({category_info})",
                                value=f"{max_wind:.1f}km/h",
                                date=dates[max_wind_idx],
                                raw_value=float(max_wind),
                            )
                        )
                    else:
                        records.append(
                            ExtremeRecord(
                                category="💨 Szél",
                                record_type="🌪️ Legszelesebb nap",
                                value=f"{max_wind:.1f}km/h",
                                date=dates[max_wind_idx],
                                raw_value=float(max_wind),
                            )
                        )

        except Exception as e:
            logger.error(f"Széllökés rekordok hiba: {e}")

        return records

    @staticmethod
    def _get_wind_data(daily_data: Dict[str, List]) -> Tuple[Optional[List], str]:
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

    def calculate_wind_speed_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Átlagszél rekordok (külön a széllökéstől)."""
        records = []

        try:
            # windspeed_10m_max vagy windspeed
            speed_list = daily_data.get("windspeed_10m_max", []) or daily_data.get(
                "windspeed", []
            )
            if speed_list and len(speed_list) == len(dates):
                clean_speed = [
                    (i, s) for i, s in enumerate(speed_list) if s is not None
                ]
                if clean_speed:
                    max_idx, max_speed = max(clean_speed, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="💨 Átlagszél",
                            record_type="🌬️ Legszelesebb nap",
                            value=f"{max_speed:.1f}km/h",
                            date=dates[max_idx],
                            raw_value=float(max_speed),
                        )
                    )
        except Exception as e:
            logger.error(f"Átlagszél rekordok hiba: {e}")

        return records

    def calculate_humidity_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Páratartalom rekordok."""
        records = []

        try:
            humidity_max = daily_data.get("relative_humidity_2m_max", [])
            humidity_min = daily_data.get("relative_humidity_2m_min", [])

            if humidity_max and len(humidity_max) == len(dates):
                clean_max = [
                    (i, h) for i, h in enumerate(humidity_max) if h is not None
                ]
                if clean_max:
                    max_idx, max_hum = max(clean_max, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="💧 Páratartalom",
                            record_type="🌫️ Legmagasabb páratartalom",
                            value=f"{max_hum:.0f}%",
                            date=dates[max_idx],
                            raw_value=float(max_hum),
                        )
                    )

            if humidity_min and len(humidity_min) == len(dates):
                clean_min = [
                    (i, h) for i, h in enumerate(humidity_min) if h is not None
                ]
                if clean_min:
                    min_idx, min_hum = min(clean_min, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="💧 Páratartalom",
                            record_type="🏜️ Legalacsonyabb páratartalom",
                            value=f"{min_hum:.0f}%",
                            date=dates[min_idx],
                            raw_value=float(min_hum),
                        )
                    )
        except Exception as e:
            logger.error(f"Páratartalom rekordok hiba: {e}")

        return records

    def calculate_pressure_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Légnyomás rekordok."""
        records = []

        try:
            pressure_max = daily_data.get("surface_pressure_max", [])
            pressure_min = daily_data.get("surface_pressure_min", [])

            if pressure_max and len(pressure_max) == len(dates):
                clean_max = [
                    (i, p) for i, p in enumerate(pressure_max) if p is not None
                ]
                if clean_max:
                    max_idx, max_press = max(clean_max, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="🔵 Légnyomás",
                            record_type="⬆️ Legmagasabb nyomás",
                            value=f"{max_press:.0f}hPa",
                            date=dates[max_idx],
                            raw_value=float(max_press),
                        )
                    )

            if pressure_min and len(pressure_min) == len(dates):
                clean_min = [
                    (i, p) for i, p in enumerate(pressure_min) if p is not None
                ]
                if clean_min:
                    min_idx, min_press = min(clean_min, key=lambda x: x[1])
                    records.append(
                        ExtremeRecord(
                            category="🔵 Légnyomás",
                            record_type="⬇️ Legalacsonyabb nyomás",
                            value=f"{min_press:.0f}hPa",
                            date=dates[min_idx],
                            raw_value=float(min_press),
                        )
                    )
        except Exception as e:
            logger.error(f"Légnyomás rekordok hiba: {e}")

        return records

    def calculate_sunshine_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Napsütés rekordok."""
        records = []

        try:
            sunshine = daily_data.get("sunshine_duration", [])
            if sunshine and len(sunshine) == len(dates):
                clean_sun = [
                    (i, s) for i, s in enumerate(sunshine) if s is not None and s > 0
                ]
                if clean_sun:
                    max_idx, max_sun = max(clean_sun, key=lambda x: x[1])
                    hours = max_sun / 3600  # másodpercből óra
                    records.append(
                        ExtremeRecord(
                            category="☀️ Napsütés",
                            record_type="🌞 Leghosszabb napsütés",
                            value=f"{hours:.1f}óra",
                            date=dates[max_idx],
                            raw_value=float(max_sun),
                        )
                    )
        except Exception as e:
            logger.error(f"Napsütés rekordok hiba: {e}")

        return records

    def calculate_uv_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """UV index rekordok."""
        records = []

        try:
            uv_max = daily_data.get("uv_index_max", [])
            if uv_max and len(uv_max) == len(dates):
                clean_uv = [(i, u) for i, u in enumerate(uv_max) if u is not None]
                if clean_uv:
                    max_idx, max_uv = max(clean_uv, key=lambda x: x[1])
                    # UV kategória
                    if max_uv >= 11:
                        uv_cat = "Extrém"
                    elif max_uv >= 8:
                        uv_cat = "Nagyon erős"
                    elif max_uv >= 6:
                        uv_cat = "Erős"
                    elif max_uv >= 3:
                        uv_cat = "Mérsékelt"
                    else:
                        uv_cat = "Gyenge"
                    records.append(
                        ExtremeRecord(
                            category="🟡 UV Index",
                            record_type=f"☀️ Legmagasabb UV ({uv_cat})",
                            value=f"{max_uv:.1f}",
                            date=dates[max_idx],
                            raw_value=float(max_uv),
                        )
                    )
        except Exception as e:
            logger.error(f"UV index rekordok hiba: {e}")

        return records
