#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations


class TestTimingAttackProtection:
    """Tests for timing attack protection in API key verification."""

    def test_compare_digest_used_in_verify(self):
        """Verify that secrets.compare_digest is used for key comparison."""
        import inspect

        from src.api.main import verify_api_key

        source = inspect.getsource(verify_api_key)
        assert "compare_digest" in source

    def test_compare_digest_in_middleware(self):
        """Verify that secrets.compare_digest is used in middleware."""
        import inspect

        from src.api.main import auth_middleware

        source = inspect.getsource(auth_middleware)
        assert "compare_digest" in source
