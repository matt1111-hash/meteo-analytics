# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from yearly_calculator.py."""

from __future__ import annotations

from .yearly_calculator_support import *


class YearlyCalculator:
    """
    🗓️ Éves rekordok és klíma trendek számítása
    """

    @staticmethod
    def _build_dataframe(daily_data: Dict[str, List], dates: List[str]):
        """Build yearly aggregation dataframe."""
        import pandas as pd

        df_data = {"date": dates}
        for key, values in daily_data.items():
            if key != "time" and values:
                df_data[key] = values[: len(dates)]
        df = pd.DataFrame(df_data)
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year
        return df

    @staticmethod
    def _append_temperature_records(df, records: List[ExtremeRecord]) -> None:
        """Append yearly temperature records."""
        if "temperature_2m_max" in df.columns:
            yearly_temp_max = df.groupby("year")["temperature_2m_max"].max()
            if not yearly_temp_max.empty:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb év",
                        value=f"{yearly_temp_max.max():.1f}°C",
                        date=str(yearly_temp_max.idxmax()),
                        raw_value=float(yearly_temp_max.max()),
                    )
                )

                yearly_temp_avg = df.groupby("year")["temperature_2m_max"].mean()
                records.append(
                    ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="📈 Legmelegebb átlag év",
                        value=f"{yearly_temp_avg.max():.1f}°C",
                        date=str(yearly_temp_avg.idxmax()),
                        raw_value=float(yearly_temp_avg.max()),
                    )
                )

        if "temperature_2m_min" in df.columns:
            yearly_temp_min = df.groupby("year")["temperature_2m_min"].min()
            if not yearly_temp_min.empty:
                records.append(
                    ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb év",
                        value=f"{yearly_temp_min.min():.1f}°C",
                        date=str(yearly_temp_min.idxmin()),
                        raw_value=float(yearly_temp_min.min()),
                    )
                )

    @staticmethod
    def _append_precipitation_records(df, records: List[ExtremeRecord]) -> None:
        """Append yearly precipitation records."""
        if "precipitation_sum" not in df.columns:
            return
        yearly_precip = df.groupby("year")["precipitation_sum"].sum()
        if yearly_precip.empty:
            return
        records.extend(
            [
                ExtremeRecord(
                    category="🌧️ Csapadék",
                    record_type="💧 Legcsapadékosabb év",
                    value=f"{yearly_precip.max():.0f}mm",
                    date=str(yearly_precip.idxmax()),
                    raw_value=float(yearly_precip.max()),
                ),
                ExtremeRecord(
                    category="🌧️ Csapadék",
                    record_type="🏜️ Legszárazabb év",
                    value=f"{yearly_precip.min():.0f}mm",
                    date=str(yearly_precip.idxmin()),
                    raw_value=float(yearly_precip.min()),
                ),
            ]
        )

    @staticmethod
    def _append_wind_records(df, records: List[ExtremeRecord]) -> None:
        """Append yearly wind records."""
        wind_col = _get_wind_column(df.columns)
        if not wind_col:
            return
        yearly_wind_max = df.groupby("year")[wind_col].max()
        if yearly_wind_max.empty:
            return

        windiest_year = yearly_wind_max.idxmax()
        windiest_speed = yearly_wind_max.max()
        if wind_col == "wind_gusts_max":
            from ..utils import WindGustsAnalyzer, WindGustsConstants

            analyzer = WindGustsAnalyzer()
            category = analyzer.categorize_wind_gust(windiest_speed, wind_col)
            category_info = WindGustsConstants.CATEGORIES.get(category, "ISMERETLEN")
            records.append(
                ExtremeRecord(
                    category="🌪️ Széllökés",
                    record_type=f"🚨 Legszelesebb év ({category_info})",
                    value=f"{windiest_speed:.1f}km/h",
                    date=str(windiest_year),
                    raw_value=float(windiest_speed),
                )
            )
            return

        records.append(
            ExtremeRecord(
                category="💨 Szél",
                record_type="🌪️ Legszelesebb év",
                value=f"{windiest_speed:.1f}km/h",
                date=str(windiest_year),
                raw_value=float(windiest_speed),
            )
        )

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
            df = YearlyCalculator._build_dataframe(daily_data, dates)
            records: List[ExtremeRecord] = []
            years = sorted(df["year"].unique())

            logger.info(
                f"Éves rekordok számítása: {len(years)} év ({years[0]}-{years[-1]})"
            )
            YearlyCalculator._append_temperature_records(df, records)
            YearlyCalculator._append_precipitation_records(df, records)
            YearlyCalculator._append_wind_records(df, records)

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
