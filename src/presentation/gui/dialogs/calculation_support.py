# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogs - Calculation

📊 Extrém értékek számítása

Képességek:
- Adatkinyerés
- Napi/havi extrém értékek számítása

Fájl: src/presentation/gui/dialogs/calculation.py
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass

from .table_handler import (
    _populate_extreme_table,
    _show_calculation_error,
    _show_no_data_message,
)
