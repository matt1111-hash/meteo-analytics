#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient


class TestOpenAPIDocs:
    """Tests for OpenAPI documentation endpoints (public)."""

    @pytest.mark.anyio
    async def test_docs_endpoint_no_auth_required(self, app):
        """Docs endpoint should work without API key."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/docs")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.anyio
    async def test_openapi_json_no_auth_required(self, app):
        """OpenAPI JSON should work without API key."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK
