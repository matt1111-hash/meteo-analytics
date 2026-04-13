#!/usr/bin/env python3
# mypy: ignore-errors

"""
Extreme Weather Calculator - Monthly Calculator
📅 Havi rekordok számítása
"""

import logging

from .extreme_records import ExtremeRecord

logger = logging.getLogger(__name__)


class MonthlyCalculator:
    """
    📅 Havi rekordok számítása
    """

    @staticmethod
    def _build_dataframe(daily_data: dict[str, list], dates: list[str]):
        """Build monthly aggregation dataframe."""
        import pandas as pd

        df_data = {"date": dates}
        for key, values in daily_data.items():
            if key != "time" and values:
                df_data[key] = values[: len(dates)]
        df = pd.DataFrame(df_data)
        df["date"] = pd.to_datetime(df["date"])
        df["year_month"] = df["date"].dt.to_period("M")
        return df

    @staticmethod
    def _append_temperature_records(df, records: list[ExtremeRecord]) -> None:
        """Append temperature-based monthly records."""
        if "temperature_2m_max" in df.columns:
            monthly_temp_max = df.groupby("year_month")["temperature_2m_max"].max()
            if not monthly_temp_max.empty:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb hónap",
                        value=f"{monthly_temp_max.max():.1f}°C",
                        date=str(monthly_temp_max.idxmax()),
                        raw_value=float(monthly_temp_max.max()),
                    )
                )
        if "temperature_2m_min" in df.columns:
            monthly_temp_min = df.groupby("year_month")["temperature_2m_min"].min()
            if not monthly_temp_min.empty:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb hónap",
                        value=f"{monthly_temp_min.min():.1f}°C",
                        date=str(monthly_temp_min.idxmin()),
                        raw_value=float(monthly_temp_min.min()),
                    )
                )

    @staticmethod
    def _append_precipitation_records(df, records: list[ExtremeRecord]) -> None:
        """Append precipitation-based monthly records."""
        if "precipitation_sum" not in df.columns:
            return
        monthly_precip = df.groupby("year_month")["precipitation_sum"].sum()
        if monthly_precip.empty:
            return
        records.extend(
            [
                ExtremeRecord(
                    category="🌧️ Csapadék",
                    record_type="💧 Legcsapadékosabb hónap",
                    value=f"{monthly_precip.max():.1f}mm",
                    date=str(monthly_precip.idxmax()),
                    raw_value=float(monthly_precip.max()),
                ),
                ExtremeRecord(
                    category="🌧️ Csapadék",
                    record_type="🏜️ Legszárazabb hónap",
                    value=f"{monthly_precip.min():.1f}mm",
                    date=str(monthly_precip.idxmin()),
                    raw_value=float(monthly_precip.min()),
                ),
            ]
        )

    @staticmethod
    def _append_wind_records(df, records: list[ExtremeRecord]) -> None:
        """Append wind-based monthly records."""
        wind_col = _get_wind_column(df.columns)
        if not wind_col:
            return
        monthly_wind = df.groupby("year_month")[wind_col].max()
        if monthly_wind.empty:
            return

        windiest_month = monthly_wind.idxmax()
        windiest_speed = monthly_wind.max()
        if wind_col == "wind_gusts_max":
            from ..utils import WindGustsAnalyzer, WindGustsConstants

            analyzer = WindGustsAnalyzer()
            category = analyzer.categorize_wind_gust(windiest_speed, wind_col)
            category_info = WindGustsConstants.CATEGORIES.get(category, "ISMERETLEN")
            records.append(
                ExtremeRecord(
                    category="🌪️ Széllökés",
                    record_type=f"🚨 Legszelesebb hónap ({category_info})",
                    value=f"{windiest_speed:.1f}km/h",
                    date=str(windiest_month),
                    raw_value=float(windiest_speed),
                )
            )
            return

        records.append(
            ExtremeRecord(
                category="💨 Szél",
                record_type="🌪️ Legszelesebb hónap",
                value=f"{windiest_speed:.1f}km/h",
                date=str(windiest_month),
                raw_value=float(windiest_speed),
            )
        )

    @staticmethod
    def calculate_records(
        daily_data: dict[str, list], dates: list[str], daily_calculator
    ) -> list[ExtremeRecord]:
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
            df = MonthlyCalculator._build_dataframe(daily_data, dates)
            records: list[ExtremeRecord] = []
            MonthlyCalculator._append_temperature_records(df, records)
            MonthlyCalculator._append_precipitation_records(df, records)
            MonthlyCalculator._append_wind_records(df, records)

            logger.info(f"Havi rekordok számítva: {len(records)} rekord")
            return records

        except Exception as e:
            logger.error(f"Havi rekordok számítási hiba: {e}")
            # Fallback: napi számítás
            return daily_calculator(daily_data, dates)


def _get_wind_column(columns) -> str | None:
    """Széllökés oszlop kiválasztása DataFrame-hez."""
    if "wind_gusts_max" in columns:
        return "wind_gusts_max"
    elif "windspeed_10m_max" in columns:
        return "windspeed_10m_max"
    elif "windspeed" in columns:
        return "windspeed"
    return None
