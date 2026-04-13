# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider Routing - Smart provider selection és routing

Kezeli a provider kiválasztást, usage tracking-et és
a fallback stratégiákat az Open-Meteo és Meteostat között.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional
