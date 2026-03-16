#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Quick Overview Tab - Re-export Module

Ez a modul backward compatibility-t biztosít.
Használd helyette: src.presentation.gui.results_panel.quick_overview_tab

Fájl: src/presentation/gui/results_panel/quick_overview_tab.py
"""

from src.presentation.gui.results_panel.quick_overview_tab.core import QuickOverviewTab

__all__ = ["QuickOverviewTab"]
