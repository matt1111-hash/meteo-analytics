#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Refactored Module
📊 Extrém időjárási értékek számítása - Moduláris struktúrával

Modulok:
- extreme_records: Adatstruktúrák (ExtremeRecord, RecordsTextSummary)
- period_calculators: Időszak alapú számítások
- category_calculators: Kategória alapú számítások
- text_generators: Szöveges generátorok
- extreme_calculator: Fő API osztály
"""

from .extreme_calculator import ExtremeCalculator
from .extreme_records import ExtremeRecord, RecordsTextSummary

__all__ = [
    'ExtremeRecord',
    'RecordsTextSummary',
    'ExtremeCalculator',
]
