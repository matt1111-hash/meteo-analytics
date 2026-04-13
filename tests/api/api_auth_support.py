#!/usr/bin/env python3

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

import pytest


@pytest.fixture
def app():
    """Create FastAPI app."""
    from src.api.main import app  # noqa: PLC0415

    return app
