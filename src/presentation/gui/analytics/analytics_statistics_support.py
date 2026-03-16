# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics Statistics Module.
Statisztika számító és megjelenítő függvények.

📊 STATISZTIKA SZÁMÍTÁSOK:
✅ Hőmérséklet statisztikák
✅ Csapadék statisztikák
✅ Szél statisztikák (BEAUFORT)
✅ Időszak statisztikák
✅ Rekord számítások
"""

import logging
from typing import Any, Dict, List, Optional

from .analytics_helpers import safe_avg, safe_count, safe_max, safe_min, safe_sum

logger = logging.getLogger(__name__)
