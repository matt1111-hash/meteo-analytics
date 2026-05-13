"""Shared pytest fixtures for API route tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from src.api.dependencies import ServiceRegistry, get_services


@pytest.fixture
def app():
    """Create FastAPI app for API tests."""
    from src.api.main import app as fastapi_app  # noqa: PLC0415

    return fastapi_app


@pytest.fixture
def mock_services() -> MagicMock:
    """Create a mock ServiceRegistry for dependency override."""
    return MagicMock(spec=ServiceRegistry)


@pytest.fixture
def app_with_deps(mock_services: MagicMock):
    """Create FastAPI app with mocked service dependencies."""
    from src.api.main import app as fastapi_app  # noqa: PLC0415

    fastapi_app.dependency_overrides[get_services] = lambda: mock_services
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()
