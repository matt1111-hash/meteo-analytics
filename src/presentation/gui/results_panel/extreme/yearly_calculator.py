# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""
Extreme Weather Calculator - Yearly Calculator
Éves rekordok és klíma trendek számítása.
"""

from __future__ import annotations

from .yearly_calculator_support import *


def _resolve_temperature_trend_column(df) -> str | None:
    """Resolve or build temperature column for trend calculation."""
    if "temperature_2m_mean" in df.columns:
        return "temperature_2m_mean"
    if "temperature_2m_max" in df.columns and "temperature_2m_min" in df.columns:
        df["temp_calculated_mean"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2
        return "temp_calculated_mean"
    return None


def _build_temperature_trend_record(temp_trend: float, years: List[int]) -> ExtremeRecord:
    """Build climate trend record for the given delta."""
    if temp_trend > 0.5:  # noqa: PLR2004
        return ExtremeRecord(
            category="🌡️ Trend",
            record_type="🔥 Felmelegedés trend",
            value=f"+{temp_trend:.1f}°C",
            date=f"{years[0]}-{years[-1]}",
            raw_value=float(temp_trend),
        )
    if temp_trend < -0.5:  # noqa: PLR2004
        return ExtremeRecord(
            category="🌡️ Trend",
            record_type="🧊 Lehűlés trend",
            value=f"{temp_trend:.1f}°C",
            date=f"{years[0]}-{years[-1]}",
            raw_value=float(temp_trend),
        )
    return ExtremeRecord(
        category="🌡️ Trend",
        record_type="📊 Stabil hőmérséklet",
        value=f"{temp_trend:+.1f}°C",
        date=f"{years[0]}-{years[-1]}",
        raw_value=float(temp_trend),
    )


def _calculate_climate_trends(df, years: List[int]) -> List[ExtremeRecord]:
    """Klímaváltozási trendek számítása 10+ évre."""
    records = []

    try:
        # Egyszerű trend számítás (első 5 év vs utolsó 5 év)
        early_years = years[:5]
        late_years = years[-5:]
        temp_col = _resolve_temperature_trend_column(df)
        if temp_col is not None:
            early_avg = df[df["year"].isin(early_years)][temp_col].mean()
            late_avg = df[df["year"].isin(late_years)][temp_col].mean()
            temp_trend = late_avg - early_avg
            records.append(_build_temperature_trend_record(temp_trend, years))

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


class YearlyCalculator:
    """
    Éves rekordok és klíma trendek számítása
    """

    @staticmethod
    def _build_dataframe(daily_data: Dict[str, List], dates: List[str]):
        """Build yearly aggregation dataframe."""
        import pandas as pd  # noqa: PLC0415

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
            from ..utils import WindGustsAnalyzer, WindGustsConstants  # noqa: PLC0415

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
        Éves rekordok számítása hosszú időszakokra optimalizálva.

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

            logger.info(f"Éves rekordok számítása: {len(years)} év ({years[0]}-{years[-1]})")
            YearlyCalculator._append_temperature_records(df, records)
            YearlyCalculator._append_precipitation_records(df, records)
            YearlyCalculator._append_wind_records(df, records)

            # Klímaváltozási trendek (10+ év esetén)
            if len(years) >= 10:  # noqa: PLR2004
                records.extend(_calculate_climate_trends(df, years))

            logger.info(f"Éves rekordok számítva: {len(records)} rekord {len(years)} évhez")
            return records

        except Exception as e:
            logger.error(f"Éves rekordok számítási hiba: {e}")
            # Fallback: havi számítás
            return monthly_calculator.calculate_records(daily_data, dates, None)
