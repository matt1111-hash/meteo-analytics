# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Processor - DataFrame konverzió és adatfeldolgozás

Kezeli az időjárási adatok DataFrame konverzióját,
a wind speed adatok feldolgozását és a WindyDaysTab
adatok előkészítését.
"""

import logging
from typing import Any

try:
    import pandas as pd

    _pandas_available = True
except ImportError:
    _pandas_available = False
    pd = None

from PySide6.QtCore import QObject
