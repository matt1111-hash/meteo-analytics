#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trend Analytics Tab - Analysis Handlers

🚀 Trend elemzés kezelése és worker management

Képességek:
- Analysis indítása
- Worker signal kezelése
- Eredmények megjelenítése
- Hiba kezelése

Fájl: src/presentation/gui/trend_analytics/trend_analytics_tab/analysis_handlers.py
"""

import logging
from typing import TYPE_CHECKING, Dict

from PySide6.QtCore import Signal

if TYPE_CHECKING:
    from ...trend_widgets import EnhancedStatisticsPanel, InteractiveTrendChart


logger = logging.getLogger(__name__)


class TrendAnalysisHandlerMixin:
    """
    Trend elemzés kezelése keverék osztály.

    Ez a mixin osztály tartalmazza a trend elemzéshez
    kapcsolódó metódusokat.
    """

    # These will be set when mixed into TrendAnalyticsTab
    analyze_button: any
    progress_bar: any
    chart: "InteractiveTrendChart"
    statistics_panel: "EnhancedStatisticsPanel"
    location_combo: any
    parameter_combo: any
    time_combo: any

    # Signals (delegált)
    analysis_started: Signal
    analysis_completed: Signal
    error_occurred: Signal
    location_selected: Signal

    # State
    current_worker: any

    def start_trend_analysis(self) -> None:
        """🚀 ENHANCED TREND ELEMZÉS INDÍTÁSA"""
        try:
            # Input validation
            location = self.location_combo.currentText().strip()
            parameter = self.parameter_combo.currentText()
            time_range = self.time_combo.currentText()

            if not location:
                self.error_occurred.emit("Kérlek válassz várost!")
                return

            if len(location) < 2:
                self.error_occurred.emit("Legalább 2 karakteres város név szükséges!")
                return

            logger.info(f"🚀 ENHANCED TREND ANALYSIS START: {location} - {parameter} - {time_range}")

            # UI update
            self.analyze_button.setEnabled(False)
            self.analyze_button.setText("⏳ Dashboard Elemzés folyamatban...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Signal emission
            self.analysis_started.emit()

            # Import here to avoid circular dependency
            from ..trend_worker import TrendAnalyticsWorker

            # Worker thread létrehozása
            self.current_worker = TrendAnalyticsWorker(location, parameter, time_range)

            # Worker signals connecting
            self.current_worker.progress_updated.connect(self.progress_bar.setValue)
            self.current_worker.data_received.connect(self.on_analysis_completed)
            self.current_worker.error_occurred.connect(self.on_analysis_error)
            self.current_worker.finished.connect(self.on_worker_finished)

            # Worker start
            self.current_worker.start()

        except Exception as e:
            logger.error(f"❌ Enhanced trend analysis start hiba: {e}")
            self.on_analysis_error(f"Elemzés indítási hiba: {str(e)}")

    def on_analysis_completed(self, trend_results: Dict) -> None:
        """🎉 ENHANCED TREND ELEMZÉS BEFEJEZÉSE"""
        try:
            logger.info(f"🎉 ENHANCED TREND ANALYSIS COMPLETED: {trend_results['settlement_name']}")

            # 🎨 PLOTLY CHART FRISSÍTÉSE
            self.chart.update_chart(trend_results)
            logger.info("✅ Plotly chart frissítve")

            # 🎯 DASHBOARD KPI KÁRTYÁK FRISSÍTÉSE
            logger.info("🎯 Dashboard KPI kártyák frissítése kezdése...")
            self.statistics_panel.update_statistics(trend_results)
            logger.info("✅ Dashboard KPI kártyák frissítve")

            # Signal emission
            self.analysis_completed.emit(trend_results)

        except Exception as e:
            logger.error(f"❌ Enhanced analysis completion handling hiba: {e}")
            self.on_analysis_error(f"Eredmény feldolgozási hiba: {str(e)}")

    def on_analysis_error(self, error_message: str) -> None:
        """❌ ENHANCED TREND ELEMZÉS HIBA KEZELÉSE"""
        logger.error(f"❌ ENHANCED TREND ANALYSIS ERROR: {error_message}")

        # Error display in Plotly chart
        self.chart.show_error_chart(error_message)

        # Error display in KPI cards
        self.statistics_panel.show_error_cards(error_message)

        # Signal emission
        self.error_occurred.emit(error_message)

    def on_worker_finished(self) -> None:
        """Worker thread befejezése (VÁLTOZATLAN)"""
        # UI reset
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🚀 Dashboard Elemzés Indítása")
        self.progress_bar.setVisible(False)

        # Worker cleanup
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None

        logger.info("✅ Enhanced worker thread finished and cleaned up")
