# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for layer_builder.py."""

from __future__ import annotations

from .layer_builder_part1 import LayerBuilderPart1Mixin
from .layer_builder_part2 import LayerBuilderPart2Mixin
from .layer_builder_support import *


class LayerBuilder(LayerBuilderPart1Mixin, LayerBuilderPart2Mixin):
    """
    🗺️ Térkép layer építő.
    """


# Export
__all__ = [
    "LayerBuilder",
]
