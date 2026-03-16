# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for SignalManager."""

from __future__ import annotations

from .signal_manager_support import *


class SignalManagerPart2Mixin:
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
