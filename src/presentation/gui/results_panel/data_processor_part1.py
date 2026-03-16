# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for DataProcessor."""

from __future__ import annotations

from .data_processor_support import *


def _find_fallback_wind_source(daily_data: Dict[str, Any]) -> tuple[Any, Any]:
    """Find first usable fallback wind source."""
    for key in ["wind_gusts_10m_max", "windspeed_10m_max", "wind_speed"]:
        if key in daily_data and daily_data[key]:
            return daily_data[key], key
    return None, None


def _build_fallback_dataframe(
    times: list[Any], wind_data: Any, wind_source: str
) -> Any:
    """Build fallback dataframe for wind data."""
    import pandas as pd

    return pd.DataFrame(
        {
            "date": times,
            "wind_speed": wind_data,
            "wind_gusts_max": wind_data,
            "wind_data_source": [wind_source] * len(times),
        }
    )


def _extract_fallback_daily_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fallback daily or hourly payload."""
    return data.get("daily", {}) or data.get("hourly", {})


class DataProcessorPart1Mixin:
    def __init__(self, parent=None):
        """
        DataProcessor inicializálása.

        Args:
            parent: Szülő QObject
        """
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._dataframe_extractor_available = False

        # DataFrameExtractor import
        try:
            from .utils import DataFrameExtractor

            self.DataFrameExtractor = DataFrameExtractor
            self._dataframe_extractor_available = True
            self._logger.info("✅ DataFrameExtractor import successful")
        except ImportError as e:
            self._logger.warning(f"⚠️ DataFrameExtractor import failed: {e}")

    def convert_data_to_dataframe(self, data: Dict[str, Any]) -> Any:
        """
        DataFrame konverzió API válaszból DataFrameExtractor-rel.

        Args:
            data: OpenMeteo API response

        Returns:
            pandas.DataFrame: Feldolgozott időjárási adatok
        """
        try:
            self._logger.info("🔥 DataFrameExtractor.extract_safely() használata...")

            if self._dataframe_extractor_available:
                df = self.DataFrameExtractor.extract_safely(data)

                if df.empty:
                    self._logger.error(
                        "❌ DataFrameExtractor üres DataFrame-et adott vissza!"
                    )
                    return self._empty_dataframe_fallback()

                # DataFrame tartalom ellenőrzése
                self._logger.info(f"🎯 DataFrame oszlopok: {list(df.columns)}")

                # Wind speed oszlop biztosítása
                df = self._ensure_wind_speed_column(df)

                self._logger.info("✅ DataFrameExtractor.extract_safely() sikeres!")
                return df
            else:
                # Fallback konverzió
                return self._fallback_conversion(data)

        except Exception as e:
            self._logger.error(f"❌ _convert_data_to_dataframe KRITIKUS hiba: {e}")
            import traceback

            traceback.print_exc()
            return self._empty_dataframe_fallback()

    def _ensure_wind_speed_column(self, df: Any) -> Any:
        """
        Wind speed oszlop biztosítása a DataFrame-ben.

        Args:
            df: DataFrame

        Returns:
            DataFrame wind_speed oszloppal
        """
        if "wind_gusts_max" in df.columns:
            # WindyDaysTab wind_speed oszlopot vár!
            df["wind_speed"] = df["wind_gusts_max"]
            self._logger.info(
                "🔥 WIND_SPEED OSZLOP JAVÍTÁS: wind_gusts_max → wind_speed mapping!"
            )

            wind_data = df["wind_speed"].dropna()
            if len(wind_data) > 0:
                valid_winds = wind_data[wind_data > 0]
                if len(valid_winds) > 0:
                    self._logger.info(
                        f"🌪️ Wind speed range: {valid_winds.min():.1f} → {valid_winds.max():.1f} km/h"
                    )
                    self._logger.info(f"🌪️ Valid records: {len(valid_winds)}/{len(df)}")
            else:
                self._logger.error("❌ Nincs valid wind gust adat!")
        else:
            self._logger.error("❌ Nincs wind_gusts_max oszlop a DataFrame-ben!")
            # Próbáljuk meg windspeed oszlopból
            if "windspeed" in df.columns:
                df["wind_speed"] = df["windspeed"]
                self._logger.warning("⚠️ FALLBACK: windspeed → wind_speed mapping!")
            else:
                self._logger.error("❌ Nincs windspeed oszlop sem!")

        return df

    def _fallback_conversion(self, data: Dict[str, Any]) -> Any:
        """
        Fallback konverzió ha DataFrameExtractor nem elérhető.

        Args:
            data: Nyers API adatok

        Returns:
            DataFrame vagy üres dict
        """
        self._logger.error("❌ DataFrameExtractor nem elérhető - fallback konverzió")

        try:
            self._logger.info("🔥 FALLBACK: Saját DataFrame konverzió...")
            daily_data = _extract_fallback_daily_data(data)

            if not daily_data:
                self._logger.error("❌ Nincs daily vagy hourly adat!")
                return self._empty_dataframe_fallback()

            times = daily_data.get("time", [])
            if not times:
                self._logger.error("❌ Nincs time adat!")
                return self._empty_dataframe_fallback()

            wind_data, wind_source = _find_fallback_wind_source(daily_data)

            if wind_data is None:
                self._logger.error("❌ Nincs szél adat!")
                return self._empty_dataframe_fallback()

            self._logger.info(f"🎯 FALLBACK wind source: {wind_source}")
            df = _build_fallback_dataframe(times, wind_data, wind_source)
            self._logger.info(
                f"🔄 FALLBACK DataFrame: {len(df)} sor, source: {wind_source}"
            )
            return df

        except Exception as fallback_error:
            self._logger.error(f"❌ FALLBACK konverzió is sikertelen: {fallback_error}")
            return self._empty_dataframe_fallback()
