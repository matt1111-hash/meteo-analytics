#!/usr/bin/env python3
"""
Infrastructure Adapters.

Adapters convert data from outer layers to inner layer types.
Following Clean Architecture, these live in the infrastructure layer.
"""

from .city_adapter import city_dict_to_city_info, city_to_city_info

__all__ = [
    "city_dict_to_city_info",
    "city_to_city_info",
]
