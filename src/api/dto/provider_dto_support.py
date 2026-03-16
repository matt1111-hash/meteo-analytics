# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""DTOs for Provider Management API endpoints.

This module defines data transfer objects for provider-related operations
including listing providers, getting status, and managing selections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Mapping
