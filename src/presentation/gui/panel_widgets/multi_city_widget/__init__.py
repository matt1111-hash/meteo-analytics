#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-City Widget Module

🏙️ Magyar régiók és megyék választó widget

Képességek:
- Region/County mode váltás
- Single selection state management
- City queries CityManager-en keresztül

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/__init__.py
"""

# Re-export for backward compatibility
from .core import MultiCityWidget

__all__ = ["MultiCityWidget"]
