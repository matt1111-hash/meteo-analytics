#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations


class TestPublicPaths:
    """Tests for public paths configuration."""

    def test_public_paths_includes_health(self):
        """PUBLIC_PATHS should include /health."""
        from src.api.main import PUBLIC_PATHS

        assert "/health" in PUBLIC_PATHS

    def test_public_paths_includes_docs(self):
        """PUBLIC_PATHS should include /docs."""
        from src.api.main import PUBLIC_PATHS

        assert "/docs" in PUBLIC_PATHS

    def test_public_paths_includes_openapi(self):
        """PUBLIC_PATHS should include /openapi.json."""
        from src.api.main import PUBLIC_PATHS

        assert "/openapi.json" in PUBLIC_PATHS
