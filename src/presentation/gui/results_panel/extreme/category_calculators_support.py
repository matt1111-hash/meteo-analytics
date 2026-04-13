# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Category Calculators
🌡️ Kategória alapú rekord számítások (temperature/precipitation/wind)
"""

import logging
from typing import Optional

from .extreme_records import ExtremeRecord

logger = logging.getLogger(__name__)
