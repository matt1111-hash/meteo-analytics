# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Anomaly Profile Manager
Main manager class for anomaly profile CRUD operations.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..anomaly_storage import AnomalyProfileStorage
from ..anomaly_types import AnomalyProfileSettings
from .default_profiles import create_profiles_data
from .profile_actions import ProfileActions

logger = logging.getLogger(__name__)
