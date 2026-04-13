#!/usr/bin/env python3
# mypy: ignore-errors

"""
Precipitation Chart

Csapadék grafikon widget professzionális oszlopdiagram vizualizációval.

Képességek:
- Oszlopdiagram csapadék mennyiségekkel
- Színkódolt oszlopok csapadék mennyiség alapján
- Interaktív tooltip funkciók
- Statisztikai információk megjelenítése

Fájl: src/presentation/gui/charts/precipitation_chart/__init__.py
"""

from .core import PrecipitationChart

__all__ = ["PrecipitationChart"]
