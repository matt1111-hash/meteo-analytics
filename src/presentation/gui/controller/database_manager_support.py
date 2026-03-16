# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Manager - Adatbázis műveletek kezelése

Kezeli az SQLite adatbázis kapcsolatot, séma frissítéseket
és az adatok mentését városokhoz és időjárási adatokhoz.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional
