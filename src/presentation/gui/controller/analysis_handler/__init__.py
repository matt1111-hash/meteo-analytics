#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Analysis Handler Module

Analysis Handler - Analysis request kezelése

Kezeli az elemzési kéréseket, worker lifecycle-t,
és a provider routing integrációt.

Modul szerkezet:
- core.py: AnalysisHandler main class (143 sor)
- request_handler.py: Analysis kérés kezelése (107 sor)
- validator.py: Request validálás (123 sor)
- provider_integration.py: Provider routing (113 sor)
- slot_handlers.py: Slot signal kezelők (63 sor)
- result_processor.py: Eredény feldolgozás (58 sor)
- state_management.py: State management és cleanup (91 sor)

Fájl: src/presentation/gui/controller/analysis_handler/__init__.py
"""

from .core import AnalysisHandler

__all__ = ["AnalysisHandler"]
