# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Yearly Calculator
🗓️ Éves rekordok és klíma trendek számítása
"""

import logging
from typing import Dict, List

from .extreme_records import ExtremeRecord

logger = logging.getLogger(__name__)
