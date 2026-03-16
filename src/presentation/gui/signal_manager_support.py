# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal Manager Module
Felelős a GUI komponensek signal-slot kapcsolatainak központi kezeléséért.
Kiszervezi a MainWindowból a signal összekötési logikát a jobb szervezettség érdekében.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .windows.main_window import MainWindow
