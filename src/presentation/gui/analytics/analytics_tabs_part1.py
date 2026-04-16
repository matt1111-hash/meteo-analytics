# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Merged part1+part2 definitions from analytics_tabs.py."""

from __future__ import annotations

from .analytics_tabs_support import *


class TemperatureTabWidget(QWidget):
    """Temperature tab - constant heatmap (RdYlBu_r)"""

    def __init__(self):  # noqa: D107
        super().__init__()

        # HEATMAP CHART
        self.temp_heatmap = HeatmapCalendarChart()
        self.temp_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.temp_heatmap.parameter = "temperature_2m_mean"
        self.temp_heatmap.chart_title = "🌡️ Konstans Hőmérséklet Heatmap"

        self._setup_ui()
        logger.info("TemperatureTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap)")

    def _setup_ui(self):
        """Hőmérséklet konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.temp_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """Hőmérséklet konstans heatmap frissítés"""
        try:
            # Direkt adatátadás - aggregáció a heatmap chart-ban történik
            self.temp_heatmap.update_data(data)

            logger.info("🌡️ Hőmérséklet KONSTANS HEATMAP tab frissítve")

        except Exception as e:
            logger.error(f"TemperatureTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class PrecipitationTabWidget(QWidget):
    """Csapadék tab - konstans heatmap (meteorológiai színskála)"""

    def __init__(self):  # noqa: D107
        super().__init__()

        # HEATMAP CHART - CSAPADÉK VERZIÓ
        self.precip_heatmap = HeatmapCalendarChart()
        self.precip_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.precip_heatmap.parameter = "precipitation_sum"
        self.precip_heatmap.chart_title = "🌧️ Konstans Csapadék Heatmap"

        # Meteorológiai csapadék színskála
        self.precip_cmap, self.precip_norm = MeteorologicalColorMaps.get_precipitation_colormap()

        self._setup_ui()
        logger.info(
            "PrecipitationTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, 0mm=fehér)"
        )

    def _setup_ui(self):
        """Csapadék konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.precip_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """Csapadék konstans heatmap frissítés"""
        try:
            # Custom colormap beállítása
            self.precip_heatmap._custom_cmap = self.precip_cmap
            self.precip_heatmap._custom_norm = self.precip_norm
            logger.debug(f"🎨 Csapadék custom colormap beállítva: {type(self.precip_cmap)}")

            # Direkt adatátadás
            self.precip_heatmap.update_data(data)

            logger.info("🌧️ Csapadék KONSTANS HEATMAP tab frissítve (0mm=fehér)")

        except Exception as e:
            logger.error(f"PrecipitationTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class WindTabWidget(QWidget):
    """Szél tab - konstans heatmap (BEAUFORT 13 fokozat)"""

    def __init__(self):  # noqa: D107
        super().__init__()

        # HEATMAP CHART - SZÉL VERZIÓ (átlagos max)
        self.wind_heatmap = HeatmapCalendarChart()
        self.wind_heatmap.figure.set_size_inches(20, 10)
        self.wind_heatmap.parameter = "windspeed_10m_max"
        self.wind_heatmap.chart_title = "💨 Konstans Szél Heatmap (windspeed_10m_max)"

        # BEAUFORT 13 fokozat színskála
        self.wind_cmap, self.wind_norm = MeteorologicalColorMaps.get_wind_colormap()

        self._setup_ui()
        logger.info(
            "WindTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, átlagos max szél)"
        )

    def _setup_ui(self):
        """Szél konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.wind_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """Szél konstans heatmap frissítés - BEAUFORT progresszív színskála"""
        try:
            daily_data = data.get("daily", {})
            logger.debug(f"DEBUG SZÉL TAB - Elérhető daily adatok: {list(daily_data.keys())}")

            wind_param = "windspeed_10m_max"

            if not daily_data.get(wind_param):
                logger.warning("Nincs elérhető windspeed_10m_max adat")
                return

            self.wind_heatmap._custom_cmap = self.wind_cmap
            self.wind_heatmap._custom_norm = self.wind_norm
            self.wind_heatmap.parameter = wind_param
            logger.debug(
                f"🎨 Szél BEAUFORT colormap beállítva: {type(self.wind_cmap)}, param: {wind_param}"
            )

            self.wind_heatmap.update_data(data)

            logger.info("💨 Szél KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat, átlagos max)")

        except Exception as e:
            logger.error(f"WindTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class WindGustTabWidget(QWidget):
    """Max széllökés tab - konstans heatmap (BEAUFORT 13 fokozat)"""

    def __init__(self):  # noqa: D107
        super().__init__()

        # HEATMAP CHART - SZÉLLÖKÉS VERZIÓ (MAX GUSTS)
        self.windgust_heatmap = HeatmapCalendarChart()
        self.windgust_heatmap.figure.set_size_inches(20, 10)
        self.windgust_heatmap.parameter = "wind_gusts_max"
        self.windgust_heatmap.chart_title = "🌪️ Konstans Max Széllökés Heatmap (wind_gusts_max)"

        # BEAUFORT 13 fokozat színskála (ugyanaz, mint a szél tab)
        self.windgust_cmap, self.windgust_norm = MeteorologicalColorMaps.get_wind_colormap()

        self._setup_ui()
        logger.info(
            "WindGustTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, max széllökések)"
        )

    def _setup_ui(self):
        """Max széllökés konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.windgust_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """Max széllökés konstans heatmap frissítés - BEAUFORT progresszív színskála"""
        try:
            daily_data = data.get("daily", {})
            logger.debug(
                f"DEBUG MAX SZÉLLÖKÉS TAB - Elérhető daily adatok: {list(daily_data.keys())}"
            )

            windgust_param = "wind_gusts_max"

            if not daily_data.get(windgust_param):
                logger.warning("Nincs elérhető wind_gusts_max adat")
                return

            self.windgust_heatmap._custom_cmap = self.windgust_cmap
            self.windgust_heatmap._custom_norm = self.windgust_norm
            self.windgust_heatmap.parameter = windgust_param
            logger.debug(
                f"🎨 Széllökés BEAUFORT colormap beállítva: {type(self.windgust_cmap)}, param: {windgust_param}"
            )

            self.windgust_heatmap.update_data(data)

            logger.info("🌪️ Max Széllökés KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat)")

        except Exception as e:
            logger.error(f"WindGustTabWidget KONSTANS HEATMAP frissítési hiba: {e}")
