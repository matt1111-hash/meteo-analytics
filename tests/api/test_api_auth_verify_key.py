#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import status


class TestVerifyAPIKey:
    """Tests for verify_api_key function."""

    def test_returns_disabled_when_auth_not_enabled(self):
        """Should return 'disabled' when auth is not configured."""
        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = False

            result = verify_api_key(api_key=None)

            assert result == "disabled"

    def test_raises_401_when_no_key_provided(self):
        """Should raise 401 when no API key is provided."""
        from fastapi import HTTPException

        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "test-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key=None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_raises_403_when_invalid_key(self):
        """Should raise 403 when invalid API key is provided."""
        from fastapi import HTTPException

        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "correct-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key="wrong-key")

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_key_when_valid(self):
        """Should return the API key when valid."""
        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "correct-key"

            result = verify_api_key(api_key="correct-key")

            assert result == "correct-key"
