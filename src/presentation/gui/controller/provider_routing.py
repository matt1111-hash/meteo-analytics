# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for provider_routing.py."""

from __future__ import annotations

from .provider_routing_part1 import ProviderRoutingPart1Mixin
from .provider_routing_part2 import ProviderRoutingPart2Mixin
from .provider_routing_support import *


class ProviderRouting(ProviderRoutingPart1Mixin, ProviderRoutingPart2Mixin):
    """
    Provider routing kezelése.

    Felelőségek:
    - Smart provider selection (historical vs recent adatok)
    - Usage tracking és cost monitoring
    - Provider fallback strategies
    - Rate limit kezelés
    """
