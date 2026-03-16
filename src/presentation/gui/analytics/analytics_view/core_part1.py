# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for AnalyticsView."""

from __future__ import annotations

from .core_support import *


class AnalyticsViewPart1Mixin:
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
