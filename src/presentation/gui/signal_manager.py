#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal Manager Module
Felelős a GUI komponensek signal-slot kapcsolatainak központi kezeléséért.
Kiszervezi a MainWindowból a signal összekötési logikát a jobb szervezettség érdekében.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .windows.main_window import MainWindow


class SignalManager:
    """
    Kezeli az alkalmazás összes signal-slot kapcsolatát.

    Ez az osztály felelős a különböző UI komponensek (ControlPanel, ResultsPanel, stb.)
    és az AppController közötti kommunikáció létrehozásáért.
    """

    def __init__(self, main_window: "MainWindow"):
        """
        SignalManager inicializálása.

        Args:
            main_window: A MainWindow példány, amelynek a komponenseit kezeli.
        """
        self.mw = main_window

    def connect_all_signals(self) -> None:
        """
        🚨 KRITIKUS: CLEAN MVC komponensek signal-slot összekötése + ANALYTICS SIGNAL FIX + 🌍 PROVIDER STATUS SIGNALS!
        """
        print("🔗 SignalManager: Starting comprehensive signal connection...")

        self._connect_control_panel()
        self._connect_app_controller()
        self._connect_analytics_view()
        self._connect_provider_status()
        self._connect_results_panel()
        self._connect_theme_manager()

        print("🚨 ✅ SignalManager: All signals connected successfully!")

    def _connect_control_panel(self) -> None:
        """ControlPanel signal-slot kapcsolatok."""
        print(
            "🎯 SignalManager: Setting up ControlPanel → AppController connections..."
        )

        if self.mw.control_panel:
            # 🚀 KRITIKUS: Egyetlen központi kapcsolat - minden elemzési kérést az AppController kezel
            if hasattr(self.mw.control_panel, "analysis_requested"):
                self.mw.control_panel.analysis_requested.connect(
                    self.mw.controller.handle_analysis_request
                )
                print(
                    "✅ SignalManager: ControlPanel.analysis_requested → AppController.handle_analysis_request CONNECTED"
                )
            else:
                print(
                    "⚠️ SignalManager: ControlPanel.analysis_requested signal NOT FOUND!"
                )

            # 🛠 MEGSZAKÍTÁS GOMB BEKÖTÉSE
            if hasattr(self.mw.control_panel, "cancel_requested"):
                self.mw.control_panel.cancel_requested.connect(
                    self.mw.controller.stop_current_analysis
                )
                print(
                    "✅ SignalManager: ControlPanel.cancel_requested → AppController.stop_current_analysis CONNECTED"
                )
            else:
                print(
                    "⚠️ SignalManager: ControlPanel.cancel_requested signal NOT FOUND!"
                )
        else:
            print("⚠️ SignalManager: ControlPanel is None!")

    def _connect_app_controller(self) -> None:
        """AppController életciklus jelek figyelése + VÁROS ELEMZÉS ADATFOLYAM FIX."""
        print("📡 SignalManager: Connecting AppController lifecycle signals...")

        controller = self.mw.controller

        # Elemzés indulása
        if hasattr(controller, "analysis_started"):
            controller.analysis_started.connect(self.mw._on_analysis_started)
            print(
                "✅ SignalManager: AppController.analysis_started → MainWindow._on_analysis_started CONNECTED"
            )

        # 🎯 KRITIKUS: Elemzés befejezése (SIKER) - VÁROS ELEMZÉS FIX!
        if hasattr(controller, "analysis_completed"):
            controller.analysis_completed.connect(self.mw._on_analysis_completed)
            print(
                "🎯 ✅ KRITIKUS: AppController.analysis_completed → MainWindow._on_analysis_completed CONNECTED"
            )

        # Elemzés hiba
        if hasattr(controller, "analysis_failed"):
            controller.analysis_failed.connect(self.mw._on_analysis_failed)
            print(
                "✅ SignalManager: AppController.analysis_failed → MainWindow._on_analysis_failed CONNECTED"
            )

        # Elemzés megszakítva
        if hasattr(controller, "analysis_cancelled"):
            controller.analysis_cancelled.connect(self.mw._on_analysis_cancelled)
            print(
                "✅ SignalManager: AppController.analysis_cancelled → MainWindow._on_analysis_cancelled CONNECTED"
            )

        # Progress frissítések
        if hasattr(controller, "analysis_progress"):

            def _on_progress(message: str, percentage: int) -> None:
                self.mw.status_bar.showMessage(f"{message} ({percentage}%)")

            controller.analysis_progress.connect(_on_progress)
            print(
                "✅ SignalManager: AppController.analysis_progress → MainWindow._on_progress CONNECTED"
            )

    def _connect_analytics_view(self) -> None:
        """AnalyticsView signal-slot kapcsolatok visszaállítása."""
        if self.mw.analytics_panel:
            print("🚨 SignalManager: Connecting AnalyticsView signals...")

            # 🚨 KRITIKUS: Analytics View multi_city_query_requested signal
            if hasattr(self.mw.analytics_panel, "multi_city_query_requested"):

                def debug_analytics_multi_city_query_requested(
                    query_type: str, region_name: str
                ):
                    print(
                        f"🚨 DEBUG [ANALYTICS→MAIN_WINDOW]: multi_city_query_requested: {query_type}, {region_name}"
                    )

                self.mw.analytics_panel.multi_city_query_requested.connect(
                    debug_analytics_multi_city_query_requested
                )
                self.mw.analytics_panel.multi_city_query_requested.connect(
                    self.mw._handle_analytics_view_query
                )
                print(
                    "🚨 ✅ KRITIKUS: AnalyticsView.multi_city_query_requested → MainWindow._handle_analytics_view_query CONNECTED!"
                )
            else:
                print(
                    "❌ SignalManager: AnalyticsView.multi_city_query_requested signal NOT FOUND!"
                )

            # Analytics további signalok
            if hasattr(self.mw.analytics_panel, "analysis_started"):
                self.mw.analytics_panel.analysis_started.connect(
                    lambda: self.mw.status_bar.showMessage(
                        "📊 Analytics elemzés folyamatban..."
                    )
                )
                print(
                    "✅ SignalManager: AnalyticsView.analysis_started signal connected"
                )

            if hasattr(self.mw.analytics_panel, "error_occurred"):
                self.mw.analytics_panel.error_occurred.connect(
                    lambda msg: self.mw.status_bar.showMessage(
                        f"❌ Analytics hiba: {msg}"
                    )
                )
                print("✅ SignalManager: AnalyticsView.error_occurred signal connected")
        else:
            print("❌ SignalManager: Analytics panel is None - signals not connected!")

    def _connect_provider_status(self) -> None:
        """Provider status signalok bekötése."""
        print("🌍 SignalManager: Connecting Provider Status signals...")

        controller = self.mw.controller

        # Provider váltás
        controller.provider_selected.connect(self.mw._on_provider_selected)
        print(
            "✅ SignalManager: Controller.provider_selected → MainWindow._on_provider_selected CONNECTED"
        )

        # Usage statistics frissítése
        controller.provider_usage_updated.connect(self.mw._on_provider_usage_updated)
        print(
            "✅ SignalManager: Controller.provider_usage_updated → MainWindow._on_provider_usage_updated CONNECTED"
        )

        # Warning events
        controller.provider_warning.connect(self.mw._on_provider_warning)
        print(
            "✅ SignalManager: Controller.provider_warning → MainWindow._on_provider_warning CONNECTED"
        )

        # Fallback notifications
        controller.provider_fallback.connect(self.mw._on_provider_fallback)
        print(
            "✅ SignalManager: Controller.provider_fallback → MainWindow._on_provider_fallback CONNECTED"
        )

    def _connect_results_panel(self) -> None:
        """ResultsPanel signalok bekötése."""
        if self.mw.results_panel:
            # Export kérések
            if hasattr(self.mw.results_panel, "export_requested"):
                self.mw.results_panel.export_requested.connect(
                    self.mw._handle_export_request
                )
                print(
                    "✅ SignalManager: ResultsPanel.export_requested → MainWindow._handle_export_request CONNECTED"
                )
            else:
                print(
                    "⚠️ SignalManager: ResultsPanel.export_requested signal NOT FOUND!"
                )

            # Extrém időjárás kérések
            if hasattr(self.mw.results_panel, "extreme_weather_requested"):
                self.mw.results_panel.extreme_weather_requested.connect(
                    self.mw._show_extreme_weather
                )
                print(
                    "✅ SignalManager: ResultsPanel.extreme_weather_requested → MainWindow._show_extreme_weather CONNECTED"
                )
            else:
                print(
                    "⚠️ SignalManager: ResultsPanel.extreme_weather_requested signal NOT FOUND - SKIPPING"
                )
        else:
            print("⚠️ SignalManager: ResultsPanel is None!")

    def _connect_theme_manager(self) -> None:
        """ThemeManager signalok bekötése."""
        # Megjegyzés: A ThemeManager automatikusan kezeli a widgeteket, de a MainWindow
        # saját signalját (ha van) beköthetjük a belső propagáló metódusba.
        if hasattr(self.mw, "theme_changed"):
            self.mw.theme_changed.connect(self.mw._propagate_theme_change)
            print(
                "✅ SignalManager: MainWindow.theme_changed → MainWindow._propagate_theme_change CONNECTED"
            )


# Export
__all__ = ["SignalManager"]
