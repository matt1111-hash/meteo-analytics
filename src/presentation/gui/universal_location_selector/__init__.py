#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Location Selector Module

🇭🇺 Enhanced Universal Location Selector - DUAL DATABASE

Képességek:
- Kombinált keresés (3178 magyar + 44k globális)
- Magyar prioritás működik
- Flag-ek és settlement type-ok

Fájl: src/presentation/gui/universal_location_selector/__init__.py
"""

# Re-export for backward compatibility
from .core import UniversalLocationSelector
from .location_card import LocationCard

__all__ = ["UniversalLocationSelector", "LocationCard"]
