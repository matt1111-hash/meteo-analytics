#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Yearly Calculator
🗓️ Éves rekordok és klíma trendek számítása
"""

import logging
from typing import Dict, List

from .extreme_records import ExtremeRecord

logger = logging.getLogger(__name__)


class YearlyCalculator:
    """
    🗓️ Éves rekordok és klíma trendek számítása
    """

    @staticmethod
    def calculate_records(
        daily_data: Dict[str, List], dates: List[str], monthly_calculator
    ) -> List[ExtremeRecord]:
        """
        🗓️ Éves rekordok számítása hosszú időszakokra optimalizálva.

        Args:
            daily_data: Daily adatok
            dates: Dátumok listája
            monthly_calculator: Havi számító (fallback-hez)

        Returns:
            List[ExtremeRecord]: Éves rekordok
        """
        try:
            import pandas as pd

            # DataFrame létrehozása
            df_data = {"date": dates}
            for key, values in daily_data.items():
                if key != "time" and values:
                    df_data[key] = values[: len(dates)]

            df = pd.DataFrame(df_data)
            df["date"] = pd.to_datetime(df["date"])
            df["year"] = df["date"].dt.year

            records = []
            years = sorted(df["year"].unique())

            logger.info(
                f"Éves rekordok számítása: {len(years)} év ({years[0]}-{years[-1]})"
            )

            # Hőmérséklet éves rekordok
            if "temperature_2m_max" in df.columns:
                yearly_temp_max = df.groupby("year")["temperature_2m_max"].max()
                if not yearly_temp_max.empty:
                    hottest_year = yearly_temp_max.idxmax()
                    hottest_temp = yearly_temp_max.max()
                    records.append(
                        ExtremeRecord(
                            category="🌡️ Hőmérséklet",
                            record_type="🔥 Legmelegebb év",
                            value=f"{hottest_temp:.1f}°C",
                            date=str(hottest_year),
                            raw_value=float(hottest_temp),
                        )
                    )

                    # Átlag hőmérséklet trend
                    yearly_temp_avg = df.groupby("year")["temperature_2m_max"].mean()
                    warmest_avg_year = yearly_temp_avg.idxmax()
                    warmest_avg_temp = yearly_temp_avg.max()
                    records.append(
                        ExtremeRecord(
                            category="🌡️ Hőmérséklet",
                            record_type="📈 Legmelegebb átlag év",
                            value=f"{warmest_avg_temp:.1f}°C",
                            date=str(warmest_avg_year),
                            raw_value=float(warmest_avg_temp),
                        )
                    )

            if "temperature_2m_min" in df.columns:
                yearly_temp_min = df.groupby("year")["temperature_2m_min"].min()
                if not yearly_temp_min.empty:
                    coldest_year = yearly_temp_min.idxmin()
                    coldest_temp = yearly_temp_min.min()
                    records.append(
                        ExtremeRecord(
                            category="🌡️ Hőmérséklet",
                            record_type="🧊 Leghidegebb év",
                            value=f"{coldest_temp:.1f}°C",
                            date=str(coldest_year),
                            raw_value=float(coldest_temp),
                        )
                    )

            # Csapadék éves rekordok
            if "precipitation_sum" in df.columns:
                yearly_precip = df.groupby("year")["precipitation_sum"].sum()
                if not yearly_precip.empty:
                    wettest_year = yearly_precip.idxmax()
                    wettest_precip = yearly_precip.max()
                    records.append(
                        ExtremeRecord(
                            category="🌧️ Csapadék",
                            record_type="💧 Legcsapadékosabb év",
                            value=f"{wettest_precip:.0f}mm",
                            date=str(wettest_year),
                            raw_value=float(wettest_precip),
                        )
                    )

                    driest_year = yearly_precip.idxmin()
                    driest_precip = yearly_precip.min()
                    records.append(
                        ExtremeRecord(
                            category="🌧️ Csapadék",
                            record_type="🏜️ Legszárazabb év",
                            value=f"{driest_precip:.0f}mm",
                            date=str(driest_year),
                            raw_value=float(driest_precip),
                        )
                    )

            # Széllökés éves rekordok
            wind_col = _get_wind_column(df.columns)
            if wind_col:
                yearly_wind_max = df.groupby("year")[wind_col].max()
                if not yearly_wind_max.empty:
                    windiest_year = yearly_wind_max.idxmax()
                    windiest_speed = yearly_wind_max.max()

                    from ..utils import WindGustsAnalyzer, WindGustsConstants

                    if wind_col == "wind_gusts_max":
                        analyzer = WindGustsAnalyzer()
                        category = analyzer.categorize_wind_gust(
                            windiest_speed, wind_col
                        )
                        category_info = WindGustsConstants.CATEGORIES.get(
                            category, "ISMERETLEN"
                        )
                        records.append(
                            ExtremeRecord(
                                category="🌪️ Széllökés",
                                record_type=f"🚨 Legszelesebb év ({category_info})",
                                value=f"{windiest_speed:.1f}km/h",
                                date=str(windiest_year),
                                raw_value=float(windiest_speed),
                            )
                        )
                    else:
                        records.append(
                            ExtremeRecord(
                                category="💨 Szél",
                                record_type="🌪️ Legszelesebb év",
                                value=f"{windiest_speed:.1f}km/h",
                                date=str(windiest_year),
                                raw_value=float(windiest_speed),
                            )
                        )

            # Klímaváltozási trendek (10+ év esetén)
            if len(years) >= 10:
                records.extend(_calculate_climate_trends(df, years))

            logger.info(
                f"Éves rekordok számítva: {len(records)} rekord {len(years)} évhez"
            )
            return records

        except Exception as e:
            logger.error(f"Éves rekordok számítási hiba: {e}")
            # Fallback: havi számítás
            return monthly_calculator.calculate_records(daily_data, dates, None)


def _calculate_climate_trends(df, years: List[int]) -> List[ExtremeRecord]:
    """Klímaváltozási trendek számítása 10+ évre."""
    records = []

    try:
        # Egyszerű trend számítás (első 5 év vs utolsó 5 év)
        early_years = years[:5]
        late_years = years[-5:]

        if "temperature_2m_mean" in df.columns or (
            "temperature_2m_max" in df.columns and "temperature_2m_min" in df.columns
        ):
            if "temperature_2m_mean" in df.columns:
                temp_col = "temperature_2m_mean"
            else:
                df["temp_calculated_mean"] = (
                    df["temperature_2m_max"] + df["temperature_2m_min"]
                ) / 2
                temp_col = "temp_calculated_mean"

            early_avg = df[df["year"].isin(early_years)][temp_col].mean()
            late_avg = df[df["year"].isin(late_years)][temp_col].mean()
            temp_trend = late_avg - early_avg

            if temp_trend > 0.5:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Trend",
                        record_type="🔥 Felmelegedés trend",
                        value=f"+{temp_trend:.1f}°C",
                        date=f"{years[0]}-{years[-1]}",
                        raw_value=float(temp_trend),
                    )
                )
            elif temp_trend < -0.5:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Trend",
                        record_type="🧊 Lehűlés trend",
                        value=f"{temp_trend:.1f}°C",
                        date=f"{years[0]}-{years[-1]}",
                        raw_value=float(temp_trend),
                    )
                )
            else:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Trend",
                        record_type="📊 Stabil hőmérséklet",
                        value=f"{temp_trend:+.1f}°C",
                        date=f"{years[0]}-{years[-1]}",
                        raw_value=float(temp_trend),
                    )
                )

    except Exception as e:
        logger.error(f"Klíma trend számítási hiba: {e}")

    return records


def _get_wind_column(columns) -> str | None:
    """Széllökés oszlop kiválasztása DataFrame-hez."""
    if "wind_gusts_max" in columns:
        return "wind_gusts_max"
    elif "windspeed_10m_max" in columns:
        return "windspeed_10m_max"
    elif "windspeed" in columns:
        return "windspeed"
    return None
