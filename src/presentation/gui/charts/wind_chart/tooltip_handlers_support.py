# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wind Chart Tooltip Handlers - Tooltip formatting and positioning.
🎯 WIND CHART SPECIFIKUS TOOLTIP: Magyar szélkategóriák és Beaufort skála
"""

from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from src.presentation.gui.theme_manager import get_current_colors

from .wind_categories import get_wind_category, get_wind_recommendations
