# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for manager.py."""

from __future__ import annotations

from .manager_part1 import AnomalyProfileManagerPart1Mixin
from .manager_part2 import AnomalyProfileManagerPart2Mixin
from .manager_support import *


class AnomalyProfileManager(AnomalyProfileManagerPart1Mixin, AnomalyProfileManagerPart2Mixin):
    """
    Anomália profilok menedzsmentje.

    🎯 FELELŐSSÉGEK:
    ✅ Profilok CRUD műveletek
    ✅ Predefined profilok kezelése
    ✅ Aktív profil tracking
    """


__all__ = ["AnomalyProfileManager"]
