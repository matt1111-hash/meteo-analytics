#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Date Range Widget Module

📅 Dátum tartomány választó widget

Képességek:
- Date mode selection (time_range vs manual_dates)
- Multi-year dropdown (1/5/10/25/55 év)
- Manual date pickers + quick buttons

Fájl: src/presentation/gui/panel_widgets/date_range_widget/__init__.py
"""

# Re-export for backward compatibility
from .core import DateRangeWidget

__all__ = ["DateRangeWidget"]
