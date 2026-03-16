#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Provider Widget Module

Universal Weather Research Platform - Provider Selection & Usage Monitoring

🎯 ALAPÉRTELMEZETT: OPEN-METEO (INGYENES)

FUNKCIÓK:
✅ Provider kiválasztás (Open-Meteo ALAPÉRTELMEZETT, Meteostat, Auto)
✅ Real-time usage monitoring
✅ Cost tracking és warnings
✅ API limit displays
✅ Provider status indicators
✅ Clean Architecture signals

Modul szerkezet:
- core.py: ProviderWidget main class (175 sor)
- ui_builder.py: UI setup (177 sor)
- provider_data.py: Provider adatok (84 sor)
- monitoring.py: Usage monitoring (130 sor)
- public_api.py: Publikus API (154 sor)

Fájl: src/presentation/gui/panel_widgets/provider_widget/__init__.py
"""

from .core import ProviderWidget

__all__ = ["ProviderWidget"]
