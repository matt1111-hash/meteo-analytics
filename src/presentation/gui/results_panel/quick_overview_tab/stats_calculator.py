#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Overview Tab - Stats Calculator (Re-export)

Statisztika számító metódusok a gyors áttekintés tab-hoz.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/stats_calculator.py
"""

from src.presentation.gui.results_panel.quick_overview_tab.temp_precip_stats import calculate_temperature_stats
from src.presentation.gui.results_panel.quick_overview_tab.temp_precip_stats import calculate_precipitation_stats
from src.presentation.gui.results_panel.quick_overview_tab.wind_info_stats import calculate_wind_stats
from src.presentation.gui.results_panel.quick_overview_tab.wind_info_stats import update_info_labels
from src.presentation.gui.results_panel.quick_overview_tab.wind_info_stats import clear_stats

__all__ = [
    "calculate_temperature_stats",
    "calculate_precipitation_stats",
    "calculate_wind_stats",
    "update_info_labels",
    "clear_stats",
]
