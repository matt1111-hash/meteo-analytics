"""Tests for APP_ENV resolution and the missing-env warning (FIX-06)."""

from __future__ import annotations

import warnings

import pytest


@pytest.fixture(autouse=True)
def _restore_app_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Snapshot and restore APIConfig.APP_ENV around each test.

    reload() mutates the class attribute as a side effect; monkeypatch restores
    the env var but not the attribute. Without this fixture, a test that reloads
    to "production" leaks that state into sibling tests (e.g. security headers).
    """
    from src.config.api_config import APIConfig  # noqa: PLC0415

    original = APIConfig.APP_ENV
    original_env = __import__("os").environ.get("APP_ENV")
    yield
    APIConfig.APP_ENV = original
    if original_env is None:
        monkeypatch.delenv("APP_ENV", raising=False)
    else:
        monkeypatch.setenv("APP_ENV", original_env)


class TestResolveAppEnv:
    """_resolve_app_env must warn on fallback and honour an explicit value."""

    def test_warns_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When APP_ENV is unset, resolve to 'development' and emit RuntimeWarning."""
        from src.config.api_config import _resolve_app_env  # noqa: PLC0415

        monkeypatch.delenv("APP_ENV", raising=False)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            value = _resolve_app_env()

        assert value == "development"
        runtime_warnings = [w for w in caught if issubclass(w.category, RuntimeWarning)]
        assert len(runtime_warnings) == 1
        assert "APP_ENV not set" in str(runtime_warnings[0].message)

    def test_honours_explicit_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An explicitly set APP_ENV must be returned verbatim with no warning."""
        from src.config.api_config import _resolve_app_env  # noqa: PLC0415

        monkeypatch.setenv("APP_ENV", "production")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            value = _resolve_app_env()

        assert value == "production"
        assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]

    def test_honours_development_explicit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit 'development' must not warn (only the silent fallback warns)."""
        from src.config.api_config import _resolve_app_env  # noqa: PLC0415

        monkeypatch.setenv("APP_ENV", "development")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            value = _resolve_app_env()

        assert value == "development"
        assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]


class TestApiConfigReloadAppEnv:
    """reload() must propagate the same warning behaviour."""

    def test_reload_warns_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.config.api_config import APIConfig  # noqa: PLC0415

        monkeypatch.delenv("APP_ENV", raising=False)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            APIConfig.reload()

        assert APIConfig.APP_ENV == "development"
        assert any(
            issubclass(w.category, RuntimeWarning) and "APP_ENV not set" in str(w.message)
            for w in caught
        )

    def test_reload_honours_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.config.api_config import APIConfig  # noqa: PLC0415

        monkeypatch.setenv("APP_ENV", "production")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            APIConfig.reload()

        assert APIConfig.APP_ENV == "production"
        assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]
