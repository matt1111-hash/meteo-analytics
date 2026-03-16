#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Provider Management API routes.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

import anyio
import pytest
from httpx import ASGITransport, AsyncClient

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    from src.api.main import app

    return app


@pytest.fixture
def client(app):
    """Create sync wrapper around AsyncClient for API tests."""

    class SyncClientAdapter:
        def __init__(self, fastapi_app) -> None:
            self._app = fastapi_app

        def get(self, url: str, **kwargs):
            async def _request():
                async with AsyncClient(
                    transport=ASGITransport(app=self._app),
                    base_url="http://test",
                ) as async_client:
                    return await async_client.get(url, **kwargs)

            return anyio.run(_request)

        def post(self, url: str, **kwargs):
            async def _request():
                async with AsyncClient(
                    transport=ASGITransport(app=self._app),
                    base_url="http://test",
                ) as async_client:
                    return await async_client.post(url, **kwargs)

            return anyio.run(_request)

    return SyncClientAdapter(app)


@pytest.fixture
def mock_provider_config():
    """Mock provider configuration."""
    config = {
        "auto": {
            "name": "Automatikus (Smart Routing)",
            "description": "Use-case alapú automatikus provider választás",
            "icon": "🤖",
            "cost": "Optimalizált",
            "routing_logic": {
                "single_city": "open-meteo",
                "multi_city": "meteostat",
                "historical_deep": "meteostat",
                "real_time": "open-meteo",
            },
        },
        "open-meteo": {
            "name": "Open-Meteo (Ingyenes)",
            "description": "Ingyenes globális időjárási API",
            "icon": "🌍",
            "cost": "Ingyenes",
            "limitations": ["Limitált multi-city support"],
        },
        "meteostat": {
            "name": "Meteostat (Prémium)",
            "description": "Prémium API gazdag történeti adatokkal",
            "icon": "💎",
            "cost": "$10 USD/hónap",
            "features": ["10k request/hónap", "Gazdag történeti adatok"],
        },
    }
    return config


@pytest.fixture
def mock_user_preferences():
    """Mock user preferences."""
    prefs = {
        "selected_provider": "auto",
        "auto_fallback_enabled": True,
        "show_usage_warnings": True,
        "monthly_budget_usd": 10.0,
        "warning_threshold": 0.8,
    }
    return prefs
