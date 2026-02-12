#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics View - Core Module
Fő AnalyticsView widget osztály.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from src.domain.entities.analytics_models import AnalyticsResult

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ...theme_manager import (
    get_current_colors,
    get_theme_manager,
    register_widget_for_theming,
)
from .multi_city_handler import AnalyticsViewMultiCityHandler
from .statistics_cards import AnalyticsViewStatisticsCards
from .ui_builder import AnalyticsViewUIBuilder

logger = logging.getLogger(__name__)


class AnalyticsView(QWidget):
    """
    🎯 REFAKTORÁLT KONSTANS HEATMAP Analytics View - KÖZPONTI SIGNAL RENDSZERREL + DEDICATED WIND CHARTOK

    ✅ REFAKTORÁLT MŰKÖDÉS:
    - A nézet most már nem indít saját lekérdezéseket.
    - A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
    - A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
      (`update_with_multi_city_result`) keresztül küldi vissza.
    - Ezzel a nézet teljesen szinkronban van a többi modullal (Térkép, ControlPanel).
    """

    # Signalok
    analysis_started = Signal()
    analysis_completed = Signal()
    error_occurred = Signal(str)

    # 🚀 ÚJ: Signal a lekérdezés indításához a MainWindow felé
    multi_city_query_requested = Signal(str, str)  # query_type, region_name

    def __init__(self, parent=None):
        super().__init__(parent)

        # Téma kezelő
        self.theme_manager = get_theme_manager()

        # Adatok tárolása
        self.current_data = None
        self.current_location = None

        # Handler osztályok
        self.ui_builder = AnalyticsViewUIBuilder(self)
        self.multi_city_handler = AnalyticsViewMultiCityHandler(self)
        self.statistics_cards = AnalyticsViewStatisticsCards(self)

        # UI elemek
        self.location_info_label = None
        self.statistics_area = None
        self.record_summary = None
        self.climate_tabs = None
        self.status_label = None

        # 🚀 MULTI-CITY KOMPONENSEK (refaktorált)
        self.region_combo = None
        self.analysis_buttons = []

        # UI építése
        self._setup_ui()
        self._setup_theme()

        logger.info(
            "🗂️ AnalyticsView REFAKTORÁLT KONSTANS HEATMAP BEAUFORT + MAX SZÉLLÖKÉS + MULTI-CITY RÉGIÓ + DEDICATED WIND CHARTOK VERZIÓ betöltve"
        )

    def _setup_ui(self) -> None:
        """UI felépítése - konstans heatmap dashboard + refaktorált multi-city + dedicated wind chartok."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Fejléc
        header_layout = self.ui_builder.create_header()
        layout.addLayout(header_layout)

        # Lokáció információ (kompakt)
        location_group = self.ui_builder.create_location_info_group()
        layout.addWidget(location_group)

        # Fő tartalom splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Bal oldal: statisztikák + refaktorált multi-city (kompakt)
        stats_widget = self.ui_builder.create_statistics_panel()
        content_splitter.addWidget(stats_widget)

        # Jobb oldal: Tab-os klímakutató dashboard + DEDICATED WIND CHARTOK
        tab_widget = self.ui_builder.create_tab_dashboard()
        content_splitter.addWidget(tab_widget)

        # Splitter arányok - tab dashboard dominál
        content_splitter.setSizes([180, 920])
        layout.addWidget(content_splitter)

        # Állapot sáv
        self.status_label = QLabel(
            "Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést"
        )
        self.status_label.setStyleSheet("color: gray; padding: 2px; font-size: 9px;")
        layout.addWidget(self.status_label)

    def _setup_theme(self) -> None:
        """Téma beállítása."""
        register_widget_for_theming(self, "container")
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self._apply_current_theme()

    def _apply_current_theme(self) -> None:
        """Jelenlegi téma alkalmazása."""
        colors = get_current_colors()

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get("surface", "#ffffff")};
                color: {colors.get("on_surface", "#000000")};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.get("border", "#ccc")};
                border-radius: 3px;
                margin-top: 6px;
                padding-top: 3px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px 0 3px;
                color: {colors.get("primary", "#0066cc")};
            }}
        """)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése."""
        self._apply_current_theme()
        logger.debug(f"Konstans heatmap dashboard téma frissítve: {theme_name}")

    # === Multi-City signal kibocsátás ===

    def _emit_query_request(self):
        """🚀 KRITIKUS: Elküldi a lekérdezési kérést a MainWindow felé."""
        self.multi_city_handler.emit_query_request()

    # === PUBLIKUS API METÓDUSOK ===

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🎯 KONSTANS HEATMAP + DEDICATED WIND CHARTOK adatok frissítése - 6 TAB - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ.
        """
        try:
            logger.info(
                "🗂️ Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok frissítése"
            )

            # Adatok tárolása
            self.current_data = data

            # Teljes napok számítása
            daily_data = data.get("daily", {})
            dates = daily_data.get("time", [])
            total_days = len(dates)

            logger.info("🎯 KONSTANS AGGREGÁCIÓ - BEAUFORT + MAX SZÉLLÖKÉS:")
            logger.info(f"  📊 {total_days} nap → 365 téglalap minden tab-nál")

            # 🚨 KRITIKUS JAVÍTÁS: Bal oldali statisztikák frissítése
            logger.info(
                "🚨 STATISZTIKÁK JAVÍTÁS: _process_and_display_statistics() meghívása"
            )
            self.statistics_cards.process_and_display_statistics(data, total_days)

            # Rekordok frissítése (mindig napi szinten)
            from .analytics_statistics import AnalyticsStatistics

            records = AnalyticsStatistics.calculate_records(data)
            self.record_summary.update_records(records)

            # Tab widget frissítése
            if self.climate_tabs:
                self.climate_tabs.update_data(data)

            # Állapot frissítése
            self._update_status(
                f"✅ {total_days} nap → 365 téglalap - Beaufort + Max Széllökés Dashboard + DEDICATED WIND CHARTOK + STATISZTIKÁK"
            )

            # Signal
            self.analysis_completed.emit()

        except Exception as e:
            logger.error(
                f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatfrissítési hiba: {e}",
                exc_info=True,
            )
            self.error_occurred.emit(f"Adatfrissítési hiba: {str(e)}")
            self._update_status("❌ Adatfeldolgozási hiba")

    def update_with_multi_city_result(self, result: "AnalyticsResult"):
        """
        ✅ ÚJ: Frissíti a nézetet a MainWindow-tól kapott elemzési eredménnyel.
        """
        logger.info(
            f"✅ ANALYTICS_VIEW: Eredmény fogadva a MainWindow-tól: {len(result.city_results) if result and result.city_results else 0} város."
        )

        try:
            if not result or not result.city_results:
                self._update_status("❌ Nincs Multi-City eredmény")
                return

            # Fake single-city data létrehozása a heatmap-ekhez
            fake_data = (
                self.multi_city_handler.create_fake_single_city_data_from_multi_city(
                    result
                )
            )

            # Heatmap-ek frissítése
            if self.climate_tabs and fake_data:
                self.climate_tabs.update_data(fake_data)

            # Fake rekordok (Multi-City eredményekből)
            fake_records = self.multi_city_handler.create_fake_records_from_multi_city(
                result
            )
            if self.record_summary:
                self.record_summary.update_records(fake_records)

            # Status frissítése
            self._update_status(
                f"✅ Multi-City eredmény feldolgozva: {len(result.city_results)} város"
            )

            logger.info(
                f"✅ Multi-City result processed in AnalyticsView: {len(result.city_results)} cities"
            )

        except Exception as e:
            logger.error(f"❌ Multi-City result processing error: {e}")
            self._update_status(f"❌ Multi-City eredmény feldolgozási hiba: {e}")
            self.error_occurred.emit(f"Multi-City eredmény hiba: {e}")

    def clear_data(self) -> None:
        """Adatok törlése és UI visszaállítása."""
        logger.info(
            "Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok törlése"
        )

        self.current_data = None
        self.current_location = None

        # UI visszaállítása
        self.location_info_label.setText("Nincs kiválasztott lokáció")

        # Statisztikák törlése
        stats_content = QLabel("Töltse be az adatokat")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                font-size: 12px;
            }
        """)
        self.statistics_area.setWidget(stats_content)

        self._update_status(
            "Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést"
        )

    def on_location_changed(self, location) -> None:
        """Lokáció változás kezelése."""
        try:
            logger.info(f"Konstans heatmap dashboard lokáció változás: {location}")
            self.current_location = location

            # Lokáció info frissítése
            if hasattr(location, "display_name"):
                display_name = location.display_name
                coords = location.coordinates
            elif isinstance(location, dict):
                display_name = location.get("name", "Ismeretlen")
                lat = location.get("latitude", 0.0)
                lon = location.get("longitude", 0.0)
                coords = (lat, lon)
            else:
                display_name = str(location)
                coords = (0.0, 0.0)

            if coords:
                location_text = (
                    f"📍 {display_name}\n🗺️ [{coords[0]:.3f}, {coords[1]:.3f}]"
                )
            else:
                location_text = f"📍 {display_name}"

            self.location_info_label.setText(location_text)
            self._update_status(f"Lokáció beállítva: {display_name}")

        except Exception as e:
            logger.error(f"Lokció változás hiba: {e}")
            self.error_occurred.emit(f"Lokció hiba: {str(e)}")

    def on_analysis_start(self) -> None:
        """Elemzés indítása."""
        logger.info(
            "Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés indítása"
        )
        self.analysis_started.emit()
        self._update_status(
            "⏳ Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés folyamatban..."
        )

    def _update_status(self, message: str) -> None:
        """Állapot üzenet frissítése."""
        if self.status_label:
            self.status_label.setText(message)
        logger.info(
            f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK állapot: {message}"
        )

    # === TÉMA API ===

    def update_theme(self) -> None:
        """Téma manuális frissítése."""
        self._apply_current_theme()

    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi adatok lekérdezése."""
        return self.current_data

    def get_current_location(self):
        """Jelenlegi lokáció lekérdezése."""
        return self.current_location
