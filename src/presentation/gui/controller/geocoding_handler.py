# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for geocoding_handler.py."""

from __future__ import annotations

from .geocoding_handler_part1 import GeocodingHandlerPart1Mixin
from .geocoding_handler_part2 import GeocodingHandlerPart2Mixin
from .geocoding_handler_support import *


class GeocodingHandler(GeocodingHandlerPart1Mixin, GeocodingHandlerPart2Mixin, QObject):
    """
    Geocoding kezelése.

    Felelőségek:
    - Keresési kérések kezelése
    - Geocoding eredmények feldolgozása
    - Település kiválasztás kezelése
    - Display név generálás
    """

    # Signalok (ki kell kötni a fő controllerben)
    geocoding_results_ready = Signal(list)
    city_saved_to_db = Signal(dict)
    error_occurred = Signal(str)
    status_updated = Signal(str)

    # Nem kritikus hiba, nem szakítjuk meg a folyamatot
