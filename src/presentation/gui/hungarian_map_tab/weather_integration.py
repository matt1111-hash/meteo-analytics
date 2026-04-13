# mypy: ignore-errors
"""
Weather integration module for HungarianMapTab.

Ez a modul tartalmazza a weather overlay generálást és integrációt.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def set_analytics_parameter(self, parameter_name: str) -> None:
    """
    🧠 Analytics paraméter beállítása - MainWindow koordinációhoz.
    """
    print(f"🧠 DEBUG: Analytics paraméter beállítva: {parameter_name}")

    self.current_analytics_parameter = parameter_name

    self.analytics_parameter_label.setText(f"🧠 Paraméter: {parameter_name}")
    self.analytics_parameter_label.setStyleSheet("color: #8E44AD; font-weight: bold;")

    self.loading_status.setText(f"🧠 Analytics paraméter beállítva: {parameter_name}")

    print(f"✅ DEBUG: Current analytics parameter stored: {self.current_analytics_parameter}")


def set_analytics_result(self, analytics_result) -> None:
    """
    🌤️ Analytics eredmény fogadása paraméter továbbításával.
    """
    print("🌤️ DEBUG: Analytics result received")
    print(f"🧠 DEBUG: Current stored parameter: {self.current_analytics_parameter}")

    self.current_analytics_result = analytics_result

    _generate_weather_overlay_from_analytics(self, analytics_result)


def _refresh_weather_overlay(self) -> None:
    """🌤️ Weather overlay manuális frissítése."""
    print("🌤️ DEBUG: Manual weather overlay refresh requested")

    if not self.current_analytics_result:
        self.loading_status.setText("⚠️ Nincs analytics eredmény a weather overlay frissítéséhez")
        return

    _generate_weather_overlay_from_analytics(self, self.current_analytics_result)


def _generate_weather_overlay_from_analytics(self, analytics_result) -> None:  # noqa: PLR0915
    """
    🌤️ Weather overlay generálása Analytics eredményből.
    """
    try:
        if not self.weather_bridge:
            error_msg = "WeatherDataBridge nem elérhető"
            print(f"❌ DEBUG: {error_msg}")
            self._on_error_occurred(error_msg)
            return

        print("🔄 DEBUG: Generating weather overlay from analytics result...")

        self.loading_status.setText("🌤️ Weather overlay generálása...")

        # Analytics eredmény → Weather overlay konverzió
        if self.current_analytics_parameter:
            folium_format = self.weather_bridge.convert_analytics_result(
                analytics_result, self.current_analytics_parameter
            )
            print(f"🧠 DEBUG: Explicit parameter conversion: {self.current_analytics_parameter}")
        else:
            folium_format = self.weather_bridge.convert_analytics_result(analytics_result)
            print("🔄 DEBUG: Auto-detect parameter conversion")

        weather_overlay = self.weather_bridge.convert_analytics_to_weather_overlay(analytics_result)

        if not weather_overlay or not folium_format:
            error_msg = "Weather overlay konverzió sikertelen"
            print(f"❌ DEBUG: {error_msg}")
            self._on_error_occurred(error_msg)
            return

        self.current_weather_overlay = weather_overlay
        self.weather_data_available = True

        print(f"✅ DEBUG: Weather overlay generated: {weather_overlay.overlay_type}")

        # Folium map frissítése
        if self.map_visualizer and self.is_folium_ready:
            if folium_format:
                self.map_visualizer.set_weather_data(folium_format)
                print("✅ DEBUG: Weather data passed to Folium map visualizer")

                self.weather_status_label.setText(
                    f"🌤️ {weather_overlay.metadata['name']}: {weather_overlay.metadata['total_cities']} város"
                )
                self.weather_status_label.setStyleSheet("color: #27AE60;")

                self.loading_status.setText(
                    f"🌤️ Weather overlay aktív: {weather_overlay.metadata['name']}"
                )

                self.weather_data_updated.emit(weather_overlay)
            else:
                print("❌ DEBUG: Weather data format conversion failed")
                self.loading_status.setText("❌ Weather overlay formátum konverzió sikertelen")
        else:
            print("⚠️ DEBUG: Folium map not ready for weather data")
            self.loading_status.setText("⚠️ Folium térkép nem kész a weather overlay-hez")

    except Exception as e:
        error_msg = f"Weather overlay generálási hiba: {e}"
        print(f"❌ DEBUG: {error_msg}")
        import traceback

        traceback.print_exc()
        self._on_error_occurred(error_msg)


def load_weather_data_from_analytics(
    self, question_type: str, region: str = "HU", limit: int = 50
) -> None:
    """
    🌤️ Weather adatok betöltése Multi-City Engine-ből.
    """
    try:
        if not self.multi_city_engine:
            error_msg = "MultiCityEngine nem elérhető"
            print(f"❌ DEBUG: {error_msg}")
            self._on_error_occurred(error_msg)
            return

        print(f"🌤️ DEBUG: Loading weather data: {question_type}, {region}, limit={limit}")
        self.loading_status.setText(f"🌤️ Weather adatok betöltése: {question_type}...")

        # Paraméter beállítás question_type alapján
        QUERY_TYPE_TO_PARAMETER = {
            "hottest_today": "Hőmérséklet",
            "coldest_today": "Hőmérséklet",
            "windiest_today": "Szél",
            "wettest_today": "Csapadék",
            "temperature_range": "Hőmérséklet",
        }

        parameter = QUERY_TYPE_TO_PARAMETER.get(question_type, "Hőmérséklet")
        set_analytics_parameter(self, parameter)

        today = datetime.now().strftime("%Y-%m-%d")

        analytics_result = self.multi_city_engine.analyze_multi_city(
            query_type=question_type, region=region, date=today, limit=limit
        )

        if analytics_result and analytics_result.city_results:
            print(f"✅ DEBUG: Weather data loaded: {len(analytics_result.city_results)} cities")
            set_analytics_result(self, analytics_result)
        else:
            error_msg = f"Nincs weather adat: {question_type}"
            print(f"⚠️ DEBUG: {error_msg}")
            self.loading_status.setText(f"⚠️ {error_msg}")

    except Exception as e:
        error_msg = f"Weather adatok betöltési hiba: {e}"
        print(f"❌ DEBUG: {error_msg}")
        self._on_error_occurred(error_msg)


__all__ = [
    "_generate_weather_overlay_from_analytics",
    "_refresh_weather_overlay",
    "load_weather_data_from_analytics",
    "set_analytics_parameter",
    "set_analytics_result",
]
