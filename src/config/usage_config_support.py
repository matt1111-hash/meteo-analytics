# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""API usage tracking and monitoring for provider selector."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar, cast

from .api_config import APIConfig
from .paths_config import (
    USAGE_TRACKING_FILE as DEFAULT_USAGE_TRACKING_FILE,
)
from .paths_config import (
    ensure_directories as default_ensure_directories,
)
from .provider_config import ProviderConfig

LOGGER = logging.getLogger(__name__)
T = TypeVar("T")
