#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics View - Multi-City Handler Module
Multi-City régió elemzés logika és signal kibocsátás.
"""

import logging
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from src.presentation.gui.analytics.analytics_view.core import AnalyticsView


logger = logging.getLogger(__name__)


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
        self.view._update_status(
            f"🚀 Multi-City kérés elküldve: {region_name} ({query_type})"
        )

        logger.info(
            f"🚀 Multi-City query request emitted: {query_type} for {region_name}"
        )

    def create_fake_single_city_data_from_multi_city(self, analytics_result) -> Dict:
        """🎯 Fake single-city data létrehozása Multi-City eredményekből a heatmap megjelenítéshez."""
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("Nincs Multi-City eredmény a heatmap frissítéshez")
                return {}

            # Multi-City eredmények aggregálása egy fake weather data-ba
            cities = analytics_result.city_results
            question = analytics_result.question

            # Fake daily data létrehozása (365 nap)
            fake_daily_data = {
                "time": [
                    f"2024-{i // 30 + 1:02d}-{i % 30 + 1:02d}" for i in range(365)
                ],
                "temperature_2m_mean": [],
                "temperature_2m_max": [],
                "temperature_2m_min": [],
                "precipitation_sum": [],
                "windspeed_10m_max": [],
                "wind_gusts_max": [],
            }

            # Metric alapú fake data generálás
            from src.domain.value_objects.enums import AnalyticsMetric

            metric_type = (
                question.metric if question else AnalyticsMetric.TEMPERATURE_2M_MAX
            )

            for i in range(365):
                # Városok értékeinek átlaga minden napra (szimuláció)
                if metric_type == AnalyticsMetric.TEMPERATURE_2M_MAX:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data["temperature_2m_max"].append(
                        avg_val + (i % 20 - 10)
                    )
                    fake_daily_data["temperature_2m_mean"].append(avg_val - 2)
                    fake_daily_data["temperature_2m_min"].append(avg_val - 8)
                    fake_daily_data["precipitation_sum"].append(0.5)
                    fake_daily_data["windspeed_10m_max"].append(10.0)
                    fake_daily_data["wind_gusts_max"].append(15.0)

                elif metric_type == AnalyticsMetric.PRECIPITATION_SUM:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data["precipitation_sum"].append(avg_val + (i % 10))
                    fake_daily_data["temperature_2m_max"].append(20.0)
                    fake_daily_data["temperature_2m_mean"].append(15.0)
                    fake_daily_data["temperature_2m_min"].append(10.0)
                    fake_daily_data["windspeed_10m_max"].append(10.0)
                    fake_daily_data["wind_gusts_max"].append(15.0)

                elif metric_type == AnalyticsMetric.WINDSPEED_10M_MAX:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data["windspeed_10m_max"].append(avg_val + (i % 15))
                    fake_daily_data["wind_gusts_max"].append(avg_val + 5)
                    fake_daily_data["temperature_2m_max"].append(20.0)
                    fake_daily_data["temperature_2m_mean"].append(15.0)
                    fake_daily_data["temperature_2m_min"].append(10.0)
                    fake_daily_data["precipitation_sum"].append(1.0)

                else:
                    # Default értékek
                    fake_daily_data["temperature_2m_max"].append(20.0)
                    fake_daily_data["temperature_2m_mean"].append(15.0)
                    fake_daily_data["temperature_2m_min"].append(10.0)
                    fake_daily_data["precipitation_sum"].append(1.0)
                    fake_daily_data["windspeed_10m_max"].append(10.0)
                    fake_daily_data["wind_gusts_max"].append(15.0)

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

    def create_fake_records_from_multi_city(
        self, analytics_result
    ) -> Dict[str, Dict[str, str]]:
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

            if len(cities) >= 2:
                second_city = cities[1]
                records["windiest"] = {
                    "value": f"{second_city.value:.1f}km/h",
                    "date": second_city.date.strftime("%Y-%m-%d")
                    if hasattr(second_city.date, "strftime")
                    else str(second_city.date),
                }

            if len(cities) >= 3:
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
