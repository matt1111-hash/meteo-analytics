"""Shared fixtures for E2E smoke tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client wired to the FastAPI app (no real server)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
