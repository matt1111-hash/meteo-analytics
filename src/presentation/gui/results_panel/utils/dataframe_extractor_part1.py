# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for DataFrameExtractor."""

from __future__ import annotations

from .dataframe_extractor_part2 import DataFrameExtractorPart2Mixin
from .dataframe_extractor_support import *


class DataFrameExtractorPart1Mixin:
    @staticmethod
    def _extract_daily_data(data: Dict[str, Any]) -> tuple[dict[str, Any], list[Any]]:
        """Extract the daily payload and its date axis."""
        daily_data = data.get("daily", {})
        if not daily_data:
            logger.warning("Nincs 'daily' adat a válaszban")
            return {}, []

        dates = daily_data.get("time", []) or daily_data.get("date", [])
        if not dates:
            logger.warning("Nincs 'time' vagy 'date' adat a daily adatokban")
            return daily_data, []
        return daily_data, dates

    @staticmethod
    def _extract_temperature_data(
        daily_data: dict[str, Any],
    ) -> tuple[list[Any], list[Any], list[Any]]:
        """Extract temperature-related series."""
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        temp_mean = daily_data.get("temperature_2m_mean", [])
        return temp_max, temp_min, temp_mean

    @staticmethod
    def _build_temp_mean(
        temp_mean: list[Any], temp_max: list[Any], temp_min: list[Any]
    ) -> list[Any]:
        """Calculate mean temperatures when the source series is missing."""
        if temp_mean or not temp_max or not temp_min:
            return temp_mean
        logger.debug("Temp_mean számítása temp_max és temp_min alapján...")
        return [
            round((t_max + t_min) / 2, 1)
            if t_max is not None and t_min is not None
            else None
            for t_max, t_min in zip(temp_max, temp_min)
        ]

    @staticmethod
    def _extract_wind_data(
        daily_data: dict[str, Any],
    ) -> tuple[list[Any], list[Any], list[Any]]:
        """Extract supported wind-related series."""
        wind_gusts_10m_max = (
            daily_data.get("wind_gusts_10m_max", [])
            or daily_data.get("windgusts_10m_max", [])
            or daily_data.get("wind_gusts_max", [])
        )
        windspeed_10m_max = daily_data.get("windspeed_10m_max", []) or daily_data.get(
            "wind_speed_max", []
        )
        winddirection = daily_data.get(
            "winddirection_10m_dominant", []
        ) or daily_data.get("wind_direction_10m_dominant", [])
        return wind_gusts_10m_max, windspeed_10m_max, winddirection

    @staticmethod
    def _build_base_dataframe_data(
        dates: list[Any],
        temp_max: list[Any],
        temp_min: list[Any],
        temp_mean: list[Any],
        precip: list[Any],
    ) -> dict[str, Any]:
        """Build the base dataframe payload before wind data is added."""
        max_length = len(dates)
        df_data = {
            "date": dates,
            "temp_max": DataFrameExtractorPart2Mixin._ensure_length(
                temp_max, max_length
            ),
            "temp_min": DataFrameExtractorPart2Mixin._ensure_length(
                temp_min, max_length
            ),
            "precipitation": DataFrameExtractorPart2Mixin._ensure_length(
                precip, max_length
            ),
        }
        if temp_mean:
            df_data["temp_mean"] = DataFrameExtractorPart2Mixin._ensure_length(
                temp_mean, max_length
            )
        return df_data

    @staticmethod
    def _add_wind_gust_columns(
        df_data: dict[str, Any], wind_gusts_10m_max: list[Any], max_length: int
    ) -> None:
        """Populate gust-related dataframe columns."""
        has_valid_wind_gusts = bool(
            wind_gusts_10m_max
            and DataFrameExtractorPart2Mixin._has_valid_data(wind_gusts_10m_max)
        )
        if wind_gusts_10m_max:
            df_data["wind_gusts_max"] = DataFrameExtractorPart2Mixin._ensure_length(
                wind_gusts_10m_max, max_length
            )
            df_data["wind_data_source"] = ["wind_gusts_10m_max"] * max_length
            if has_valid_wind_gusts:
                logger.info(
                    "✅ SZÉLLÖKÉS: wind_gusts_10m_max (%s values)",
                    len(wind_gusts_10m_max),
                )
                return
            logger.warning(
                "⚠️ SZÉLLÖKÉS: wind_gusts_10m_max adat van (%s values), de nem érvényes numerikus formátum",
                len(wind_gusts_10m_max),
            )
            logger.warning("⚠️ Az adatok mégis felhasználásra kerülnek (fallback mód)")
            return

        df_data["wind_gusts_max"] = [None] * max_length
        df_data["wind_data_source"] = ["no_data"] * max_length
        logger.warning("❌ Nincs széllökés adat")

    @staticmethod
    def _add_windspeed_column(
        df_data: dict[str, Any],
        windspeed_10m_max: list[Any],
        wind_gusts_10m_max: list[Any],
        max_length: int,
    ) -> None:
        """Populate the windspeed column, with gust fallback when necessary."""
        has_valid_windspeed = bool(
            windspeed_10m_max
            and DataFrameExtractorPart2Mixin._has_valid_data(windspeed_10m_max)
        )
        has_valid_gusts = bool(
            wind_gusts_10m_max
            and DataFrameExtractorPart2Mixin._has_valid_data(wind_gusts_10m_max)
        )
        if has_valid_windspeed:
            df_data["windspeed"] = DataFrameExtractorPart2Mixin._ensure_length(
                windspeed_10m_max, max_length
            )
            logger.debug(
                "✅ SZÉLSEBESSÉG: windspeed_10m_max (%s values)",
                len(windspeed_10m_max),
            )
            return
        if has_valid_gusts:
            df_data["windspeed"] = df_data["wind_gusts_max"]
            logger.debug(
                "⚠️ SZÉLSEBESSÉG fallback to széllökés (%s values)",
                len(wind_gusts_10m_max),
            )
            return
        df_data["windspeed"] = [None] * max_length
        logger.debug("❌ SZÉLSEBESSÉG: NO DATA!")

    @staticmethod
    def _add_winddirection_column(
        df_data: dict[str, Any], winddirection: list[Any], max_length: int
    ) -> None:
        """Populate the wind direction column when present."""
        if not winddirection:
            return
        df_data["winddirection"] = DataFrameExtractorPart2Mixin._ensure_length(
            winddirection, max_length
        )
        logger.debug(
            "🧭 SZÉLIRÁNY: winddirection_10m_dominant (%s values)",
            len(winddirection),
        )

    @staticmethod
    def _convert_numeric_columns(df: pd.DataFrame) -> None:
        """Convert wind-related columns to numeric types."""
        for column in ["windspeed", "wind_gusts_max", "winddirection"]:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")
                logger.debug("✅ Típuskonverzió: %s → numerikus", column)

    @staticmethod
    def _log_wind_stats(df: pd.DataFrame) -> None:
        """Emit wind statistics after dataframe extraction."""
        if "wind_gusts_max" not in df.columns:
            return
        wind_data = df["wind_gusts_max"].dropna()
        if len(wind_data) == 0:
            return
        source = (
            df["wind_data_source"].iloc[0]
            if "wind_data_source" in df.columns
            else "unknown"
        )
        logger.info("🌪️ Wind stats - Source: %s", source)
        logger.info("🌪️ Wind range: %.1f → %.1f km/h", wind_data.min(), wind_data.max())

    @staticmethod
    def extract_safely(data: Dict[str, Any]) -> pd.DataFrame:
        """Convert Open-Meteo daily data into a normalized dataframe."""
        try:
            logger.debug("DataFrameExtractor.extract_safely() - START")
            daily_data, dates = DataFrameExtractorPart1Mixin._extract_daily_data(data)
            if not dates:
                return pd.DataFrame()

            logger.debug(f"Extracting {len(dates)} napok adatai...")
            temp_max, temp_min, temp_mean = (
                DataFrameExtractorPart1Mixin._extract_temperature_data(daily_data)
            )
            temp_mean = DataFrameExtractorPart1Mixin._build_temp_mean(
                temp_mean, temp_max, temp_min
            )
            precip = daily_data.get("precipitation_sum", [])
            wind_gusts_10m_max, windspeed_10m_max, winddirection = (
                DataFrameExtractorPart1Mixin._extract_wind_data(daily_data)
            )
            max_length = len(dates)
            df_data = DataFrameExtractorPart1Mixin._build_base_dataframe_data(
                dates, temp_max, temp_min, temp_mean, precip
            )
            DataFrameExtractorPart1Mixin._add_wind_gust_columns(
                df_data, wind_gusts_10m_max, max_length
            )
            DataFrameExtractorPart1Mixin._add_windspeed_column(
                df_data, windspeed_10m_max, wind_gusts_10m_max, max_length
            )
            DataFrameExtractorPart1Mixin._add_winddirection_column(
                df_data, winddirection, max_length
            )

            df = pd.DataFrame(df_data)
            DataFrameExtractorPart1Mixin._convert_numeric_columns(df)

            logger.info(f"✅ DataFrame extracted successfully: {df.shape} (rows, cols)")
            logger.debug(f"Columns: {list(df.columns)}")
            DataFrameExtractorPart1Mixin._log_wind_stats(df)

            return df

        except Exception as e:
            logger.error(f"❌ DataFrame extract hiba: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()
