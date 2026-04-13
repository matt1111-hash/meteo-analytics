#!/usr/bin/env python3
# mypy: ignore-errors

"""
Analytics View - Multi-City Handler Module
Multi-City régió elemzés logika és signal kibocsátás.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.presentation.gui.analytics.analytics_view.core import AnalyticsView


logger = logging.getLogger(__name__)


def _build_fake_daily_template() -> dict[str, list]:
    """Build the base fake daily dataset."""
    return {
        "time": [f"2024-{i // 30 + 1:02d}-{i % 30 + 1:02d}" for i in range(365)],
        "temperature_2m_mean": [],
        "temperature_2m_max": [],
        "temperature_2m_min": [],
        "precipitation_sum": [],
        "windspeed_10m_max": [],
        "wind_gusts_max": [],
    }


def _append_temperature_day(
    fake_daily_data: dict[str, list], avg_val: float, day_index: int
) -> None:
    """Append synthetic temperature-focused values for one day."""
    fake_daily_data["temperature_2m_max"].append(avg_val + (day_index % 20 - 10))
    fake_daily_data["temperature_2m_mean"].append(avg_val - 2)
    fake_daily_data["temperature_2m_min"].append(avg_val - 8)
    fake_daily_data["precipitation_sum"].append(0.5)
    fake_daily_data["windspeed_10m_max"].append(10.0)
    fake_daily_data["wind_gusts_max"].append(15.0)


def _append_precipitation_day(
    fake_daily_data: dict[str, list], avg_val: float, day_index: int
) -> None:
    """Append synthetic precipitation-focused values for one day."""
    fake_daily_data["precipitation_sum"].append(avg_val + (day_index % 10))
    fake_daily_data["temperature_2m_max"].append(20.0)
    fake_daily_data["temperature_2m_mean"].append(15.0)
    fake_daily_data["temperature_2m_min"].append(10.0)
    fake_daily_data["windspeed_10m_max"].append(10.0)
    fake_daily_data["wind_gusts_max"].append(15.0)


def _append_wind_day(fake_daily_data: dict[str, list], avg_val: float, day_index: int) -> None:
    """Append synthetic wind-focused values for one day."""
    fake_daily_data["windspeed_10m_max"].append(avg_val + (day_index % 15))
    fake_daily_data["wind_gusts_max"].append(avg_val + 5)
    fake_daily_data["temperature_2m_max"].append(20.0)
    fake_daily_data["temperature_2m_mean"].append(15.0)
    fake_daily_data["temperature_2m_min"].append(10.0)
    fake_daily_data["precipitation_sum"].append(1.0)


def _append_default_day(fake_daily_data: dict[str, list]) -> None:
    """Append default synthetic values for one day."""
    fake_daily_data["temperature_2m_max"].append(20.0)
    fake_daily_data["temperature_2m_mean"].append(15.0)
    fake_daily_data["temperature_2m_min"].append(10.0)
    fake_daily_data["precipitation_sum"].append(1.0)
    fake_daily_data["windspeed_10m_max"].append(10.0)
    fake_daily_data["wind_gusts_max"].append(15.0)


def _append_metric_day(
    fake_daily_data: dict[str, list], metric_type, avg_val: float, day_index: int
) -> None:
    """Append one synthetic day based on the selected metric."""
    from src.domain.value_objects.enums import AnalyticsMetric  # noqa: PLC0415

    if metric_type == AnalyticsMetric.TEMPERATURE_2M_MAX:
        _append_temperature_day(fake_daily_data, avg_val, day_index)
    elif metric_type == AnalyticsMetric.PRECIPITATION_SUM:
        _append_precipitation_day(fake_daily_data, avg_val, day_index)
    elif metric_type == AnalyticsMetric.WINDSPEED_10M_MAX:
        _append_wind_day(fake_daily_data, avg_val, day_index)
    else:
        _append_default_day(fake_daily_data)


class AnalyticsViewMultiCityHandler:
    """Multi-City régió elemzés kezelő osztály."""

    def __init__(self, view: "AnalyticsView"):
        """Inicializálás."""
        self.view = view

    def emit_query_request(self):
        """🚀 KRITIKUS: Elküldi a lekérdezési kérést a MainWindow felé - REFAKTORÁLT SIGNAL EMISSION."""
        sender = self.view.sender()
        query_type = sender.property("query_type")
        region_name = self.view.region_combo.currentText()

        logger.info(
            f"🚀 ANALYTICS_VIEW: Signal 'multi_city_query_requested' emitted with: {query_type}, {region_name}"
        )

        # ✅ ÚJ: Signal kibocsátása a MainWindow felé
        self.view.multi_city_query_requested.emit(query_type, region_name)

        # UI visszajelzés
        self.view._update_status(f"🚀 Multi-City kérés elküldve: {region_name} ({query_type})")

        logger.info(f"🚀 Multi-City query request emitted: {query_type} for {region_name}")

    def create_fake_single_city_data_from_multi_city(self, analytics_result) -> dict:
        """🎯 Fake single-city data létrehozása Multi-City eredményekből a heatmap megjelenítéshez."""
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("Nincs Multi-City eredmény a heatmap frissítéshez")
                return {}

            # Multi-City eredmények aggregálása egy fake weather data-ba
            cities = analytics_result.city_results
            question = analytics_result.question
            fake_daily_data = _build_fake_daily_template()

            # Metric alapú fake data generálás
            from src.domain.value_objects.enums import AnalyticsMetric  # noqa: PLC0415

            metric_type = question.metric if question else AnalyticsMetric.TEMPERATURE_2M_MAX
            avg_val = sum(city.value for city in cities) / len(cities)

            for i in range(365):
                _append_metric_day(fake_daily_data, metric_type, avg_val, i)

            # Fake data objektum
            fake_data = {
                "daily": fake_daily_data,
                "location": {
                    "name": f"Multi-City: {analytics_result.question.question_text if analytics_result.question else 'Régió Elemzés'}",
                    "latitude": 47.5,
                    "longitude": 19.0,
                },
            }

            logger.info(
                f"🎯 Fake single-city data létrehozva Multi-City eredményekből ({len(cities)} város)"
            )

            return fake_data

        except Exception as e:
            logger.error(f"❌ Fake data creation hiba: {e}")
            return {}

    def create_fake_records_from_multi_city(self, analytics_result) -> dict[str, dict[str, str]]:
        """🏆 Fake rekordok létrehozása Multi-City eredményekből."""
        try:
            if not analytics_result.city_results:
                return {}

            cities = analytics_result.city_results
            records = {}

            # Top 3 város kiválasztása különböző kategóriákhoz
            if len(cities) >= 1:
                top_city = cities[0]
                records["hottest"] = {
                    "value": f"{top_city.value:.1f}°C",
                    "date": top_city.date.strftime("%Y-%m-%d")
                    if hasattr(top_city.date, "strftime")
                    else str(top_city.date),
                }

            if len(cities) >= 2:  # noqa: PLR2004
                second_city = cities[1]
                records["windiest"] = {
                    "value": f"{second_city.value:.1f}km/h",
                    "date": second_city.date.strftime("%Y-%m-%d")
                    if hasattr(second_city.date, "strftime")
                    else str(second_city.date),
                }

            if len(cities) >= 3:  # noqa: PLR2004
                third_city = cities[2]
                records["wettest"] = {
                    "value": f"{third_city.value:.1f}mm",
                    "date": third_city.date.strftime("%Y-%m-%d")
                    if hasattr(third_city.date, "strftime")
                    else str(third_city.date),
                }

            # Default értékek
            records.setdefault("coldest", {"value": "N/A", "date": "Multi-City"})
            records.setdefault("driest", {"value": "N/A", "date": "Multi-City"})

            return records

        except Exception as e:
            logger.error(f"❌ Fake records creation hiba: {e}")
            return {}
