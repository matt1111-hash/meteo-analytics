# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for SignalManager."""

from __future__ import annotations

from .signal_manager_support import *


class SignalManagerPart1Mixin:  # noqa: D101
    def __init__(self, main_window: MainWindow):
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
        print("🎯 SignalManager: Setting up ControlPanel → AppController connections...")

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
                print("⚠️ SignalManager: ControlPanel.analysis_requested signal NOT FOUND!")

            # 🛠 MEGSZAKÍTÁS GOMB BEKÖTÉSE
            if hasattr(self.mw.control_panel, "cancel_requested"):
                self.mw.control_panel.cancel_requested.connect(
                    self.mw.controller.stop_current_analysis
                )
                print(
                    "✅ SignalManager: ControlPanel.cancel_requested → AppController.stop_current_analysis CONNECTED"
                )
            else:
                print("⚠️ SignalManager: ControlPanel.cancel_requested signal NOT FOUND!")
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

                def debug_analytics_multi_city_query_requested(query_type: str, region_name: str):
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
                    lambda: self.mw.status_bar.showMessage("📊 Analytics elemzés folyamatban...")
                )
                print("✅ SignalManager: AnalyticsView.analysis_started signal connected")

            if hasattr(self.mw.analytics_panel, "error_occurred"):
                self.mw.analytics_panel.error_occurred.connect(
                    lambda msg: self.mw.status_bar.showMessage(f"❌ Analytics hiba: {msg}")
                )
                print("✅ SignalManager: AnalyticsView.error_occurred signal connected")
        else:
            print("❌ SignalManager: Analytics panel is None - signals not connected!")
