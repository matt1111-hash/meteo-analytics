"""Shared pytest fixtures for API route tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def app():
    """Create FastAPI app for API tests."""
    from src.api.main import app as fastapi_app

    return fastapi_app
