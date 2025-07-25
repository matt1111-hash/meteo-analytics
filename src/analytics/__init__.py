#!/usr/bin/env python3
"""
Analytics Module - Magyar MVP Clean Version
==========================================
MAGYAR KLÍMAANALITIKA MVP verzió:
- Csak MultiCityEngine export (3200+ magyar település támogatás)
- AI modulok eltávolítva
- Clean, simple import structure
- Magyar MVP fókusz

Last Updated: 2025-07-23
Status: READY - Magyar MVP alapja
"""

# Multi-City Analytics Engine - Magyar MVP alapja
from .multi_city_engine import (
    MultiCityEngine, 
    MultiCityQuery
)

__all__ = [
    # Multi-City Analytics - 3200+ magyar település támogatás
    'MultiCityEngine', 
    'MultiCityQuery'
]