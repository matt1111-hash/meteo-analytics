#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Monthly Calculator
📅 Havi rekordok számítása
"""

import logging
from typing import Dict, List

from .extreme_records import ExtremeRecord

logger = logging.getLogger(__name__)


class MonthlyCalculator:
    """
    📅 Havi rekordok számítása
    """

    @staticmethod
    def calculate_records(
        daily_data: Dict[str, List],
        dates: List[str],
        daily_calculator
    ) -> List[ExtremeRecord]:
        """
        📅 Havi rekordok számítása pandas aggregációval.

        Args:
            daily_data: Daily adatok
            dates: Dátumok listája
            daily_calculator: Napi számító (fallback-hez)

        Returns:
            List[ExtremeRecord]: Havi rekordok
        """
        try:
            import pandas as pd

            # DataFrame létrehozása
            df_data = {'date': dates}
            for key, values in daily_data.items():
                if key != 'time' and values:
                    df_data[key] = values[:len(dates)]

            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df['year_month'] = df['date'].dt.to_period('M')

            records = []

            # Hőmérséklet aggregációk
            if 'temperature_2m_max' in df.columns:
                monthly_temp_max = df.groupby('year_month')['temperature_2m_max'].max()
                if not monthly_temp_max.empty:
                    hottest_month = monthly_temp_max.idxmax()
                    hottest_temp = monthly_temp_max.max()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb hónap",
                        value=f"{hottest_temp:.1f}°C",
                        date=str(hottest_month),
                        raw_value=float(hottest_temp)
                    ))

            if 'temperature_2m_min' in df.columns:
                monthly_temp_min = df.groupby('year_month')['temperature_2m_min'].min()
                if not monthly_temp_min.empty:
                    coldest_month = monthly_temp_min.idxmin()
                    coldest_temp = monthly_temp_min.min()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb hónap",
                        value=f"{coldest_temp:.1f}°C",
                        date=str(coldest_month),
                        raw_value=float(coldest_temp)
                    ))

            # Csapadék aggregációk
            if 'precipitation_sum' in df.columns:
                monthly_precip = df.groupby('year_month')['precipitation_sum'].sum()
                if not monthly_precip.empty:
                    wettest_month = monthly_precip.idxmax()
                    wettest_precip = monthly_precip.max()
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="💧 Legcsapadékosabb hónap",
                        value=f"{wettest_precip:.1f}mm",
                        date=str(wettest_month),
                        raw_value=float(wettest_precip)
                    ))

                    driest_month = monthly_precip.idxmin()
                    driest_precip = monthly_precip.min()
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="🏜️ Legszárazabb hónap",
                        value=f"{driest_precip:.1f}mm",
                        date=str(driest_month),
                        raw_value=float(driest_precip)
                    ))

            # Széllökés aggregációk
            wind_col = _get_wind_column(df.columns)
            if wind_col:
                monthly_wind = df.groupby('year_month')[wind_col].max()
                if not monthly_wind.empty:
                    windiest_month = monthly_wind.idxmax()
                    windiest_speed = monthly_wind.max()

                    from ..utils import WindGustsAnalyzer, WindGustsConstants
                    if wind_col == 'wind_gusts_max':
                        analyzer = WindGustsAnalyzer()
                        category = analyzer.categorize_wind_gust(
                            windiest_speed, wind_col
                        )
                        category_info = WindGustsConstants.CATEGORIES.get(
                            category, 'ISMERETLEN'
                        )
                        records.append(ExtremeRecord(
                            category="🌪️ Széllökés",
                            record_type=f"🚨 Legszelesebb hónap ({category_info})",
                            value=f"{windiest_speed:.1f}km/h",
                            date=str(windiest_month),
                            raw_value=float(windiest_speed)
                        ))
                    else:
                        records.append(ExtremeRecord(
                            category="💨 Szél",
                            record_type="🌪️ Legszelesebb hónap",
                            value=f"{windiest_speed:.1f}km/h",
                            date=str(windiest_month),
                            raw_value=float(windiest_speed)
                        ))

            logger.info(f"Havi rekordok számítva: {len(records)} rekord")
            return records

        except Exception as e:
            logger.error(f"Havi rekordok számítási hiba: {e}")
            # Fallback: napi számítás
            return daily_calculator(daily_data, dates)


def _get_wind_column(columns) -> str | None:
    """Széllökés oszlop kiválasztása DataFrame-hez."""
    if 'wind_gusts_max' in columns:
        return 'wind_gusts_max'
    elif 'windspeed_10m_max' in columns:
        return 'windspeed_10m_max'
    elif 'windspeed' in columns:
        return 'windspeed'
    return None
