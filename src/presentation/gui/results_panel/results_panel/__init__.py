#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Results Panel Module

Results Panel - Clean Architecture Refactor

A fő ResultsPanel osztály, ami moduláris felépítésű,
külön komponensekre bontva a funkcionális területek szerint.

Modul szerkezet:
- core.py: ResultsPanel main class (195 sor)
- ui_builder.py: UI setup (119 sor)
- signal_handlers.py: Signal kezelés (142 sor)
- public_api.py: Publikus API (227 sor)
- state_management.py: State management (129 sor)

Fájl: src/presentation/gui/results_panel/results_panel/__init__.py
"""

from .core import ResultsPanel

__all__ = ["ResultsPanel"]
