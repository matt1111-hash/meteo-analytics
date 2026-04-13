#!/usr/bin/env python3
# mypy: ignore-errors

"""
Extreme Weather Calculator - Text Generators
📋 Szöveges rekord összefoglalók generálása
"""

import logging

from .extreme_records import RecordsTextSummary

logger = logging.getLogger(__name__)


def _get_clean_indexed_values(values: list) -> list[tuple[int, float]]:
    """Return indexed non-null values."""
    return [(index, value) for index, value in enumerate(values) if value is not None]


def _build_temperature_summary(
    max_temp: float, max_date: str, min_temp: float, min_date: str
) -> str:
    """Build the temperature summary text."""
    return f"""🌡️ HŐMÉRSÉKLET REKORDOK:
   🔥 Legmelegebb nap: {max_temp:.1f}°C ({max_date})
   🧊 Leghidegebb nap: {min_temp:.1f}°C ({min_date})
   📈 Hőingás: {max_temp - min_temp:.1f}°C

"""


def _build_precipitation_summary(
    max_precip: float, max_date: str, dry_days: int, total_precip: float
) -> str:
    """Build the precipitation summary text."""
    return f"""🌧️ CSAPADÉK REKORDOK:
   💧 Legtöbb csapadék: {max_precip:.1f}mm ({max_date})
   🏜️ Száraz napok: {dry_days} nap
   📊 Összes csapadék: {total_precip:.1f}mm

"""


def _build_wind_category_line(category: str) -> str:
    """Build the warning line for gust categories."""
    from ..utils import WindGustsConstants

    if category == "hurricane":
        threshold = WindGustsConstants.HURRICANE_THRESHOLD
        return (
            f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{threshold:.0f} km/h)\n"
        )
    if category == "extreme":
        threshold = WindGustsConstants.EXTREME_THRESHOLD
        return (
            f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{threshold:.0f} km/h)\n"
        )
    if category == "strong":
        threshold = WindGustsConstants.STRONG_THRESHOLD
        return (
            f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{threshold:.0f} km/h)\n"
        )
    return f"   ✅ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]}\n"


def _build_gust_summary(max_wind_value: float, max_date: str, category: str) -> str:
    """Build the wind gust headline block."""
    return (
        f"🌪️ SZÉLLÖKÉS REKORDOK:\n"
        f"   🚨 Legerősebb széllökés: {max_wind_value:.1f}km/h ({max_date})\n"
        f"{_build_wind_category_line(category)}"
    )


def _build_wind_summary(max_wind_value: float, max_date: str) -> str:
    """Build the average-wind headline block."""
    return f"💨 SZÉL REKORDOK:\n" f"   🌪️ Legerősebb szél: {max_wind_value:.1f}km/h ({max_date})\n"


class TextGenerators:
    """
    📋 Szöveges rekord összefoglalók generálása

    Felelős:
    - Hőmérséklet szöveges összefoglaló
    - Csapadék szöveges összefoglaló
    - Széllökés szöveges összefoglaló
    """

    def generate_summary(self, daily_data: dict[str, list], dates: list[str]) -> RecordsTextSummary:
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

    def _generate_temperature_text(self, daily_data: dict[str, list], dates: list[str]) -> str:
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
                clean_max = _get_clean_indexed_values(temp_max_list)
                clean_min = _get_clean_indexed_values(temp_min_list)

                if clean_max and clean_min:
                    max_temp_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    min_temp_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    return _build_temperature_summary(
                        max_temp, dates[max_temp_idx], min_temp, dates[min_temp_idx]
                    )
            return "🌡️ HŐMÉRSÉKLET REKORDOK: Nincs megfelelő adat\n\n"
        except Exception as e:
            logger.error(f"Hőmérséklet szöveg hiba: {e}")
            return "🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n\n"

    def _generate_precipitation_text(self, daily_data: dict[str, list], dates: list[str]) -> str:
        """Csapadék szöveges összefoglaló."""
        try:
            precip_list = daily_data.get("precipitation_sum", [])

            if precip_list and len(precip_list) == len(dates):
                clean_precip = _get_clean_indexed_values(precip_list)

                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    valid_precip = [p for p in precip_list if p is not None]
                    dry_days = sum(1 for p in valid_precip if p <= 0.1)  # noqa: PLR2004
                    total_precip = sum(valid_precip)
                    return _build_precipitation_summary(
                        max_precip, dates[max_precip_idx], dry_days, total_precip
                    )
            return "🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
        except Exception as e:
            logger.error(f"Csapadék szöveg hiba: {e}")
            return "🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n\n"

    def _generate_wind_text(self, daily_data: dict[str, list], dates: list[str]) -> str:
        """Széllökés szöveges összefoglaló."""
        try:
            wind_data, wind_source = self._get_wind_data(daily_data)

            if wind_data and len(wind_data) == len(dates):
                clean_wind = _get_clean_indexed_values(wind_data)

                if clean_wind:
                    max_wind_idx, max_wind_value = max(clean_wind, key=lambda x: x[1])
                    valid_winds = [w for w in wind_data if w is not None]
                    avg_wind = sum(valid_winds) / len(valid_winds)

                    from ..utils import WindGustsAnalyzer

                    if wind_source == "wind_gusts_max":
                        category = WindGustsAnalyzer.categorize_wind_gust(
                            max_wind_value, wind_source
                        )
                        text = _build_gust_summary(max_wind_value, dates[max_wind_idx], category)
                    else:
                        text = _build_wind_summary(max_wind_value, dates[max_wind_idx])

                    text += f"   📊 Átlagos szélsebesség: {avg_wind:.1f}km/h\n"
                    text += f"   📈 Adatforrás: {wind_source}\n\n"

                    return text

            return "🌪️ SZÉLLÖKÉS REKORDOK: Nincs szél adat\n\n"
        except Exception as e:
            logger.error(f"Széllökés szöveg hiba: {e}")
            return "🌪️ SZÉLLÖKÉS REKORDOK: Hiba a számítás során\n\n"

    @staticmethod
    def _get_wind_data(daily_data: dict[str, list]) -> tuple[list | None, str]:
        """Széladatok prioritás alapú kiválasztása."""
        wind_gusts_max = daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])
        windspeed = daily_data.get("windspeed", [])

        if wind_gusts_max:
            return wind_gusts_max, "wind_gusts_max"
        if windspeed_10m_max:
            return windspeed_10m_max, "windspeed_10m_max"
        if windspeed:
            return windspeed, "windspeed"
        return None, "no_data"
