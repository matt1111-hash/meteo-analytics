# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provider selector configuration and user preferences management."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, TypeVar, cast

from .paths_config import (
    PROVIDER_PREFS_FILE as DEFAULT_PROVIDER_PREFS_FILE,
)
from .paths_config import (
    ensure_directories as default_ensure_directories,
)

LOGGER = logging.getLogger(__name__)
T = TypeVar("T")
