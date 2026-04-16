"""Közös pytest fixturek a konfigurációs tesztekhez."""

from __future__ import annotations

import builtins
import io

import pytest
from src import config


@pytest.fixture(params=["asyncio"])
def anyio_backend() -> str:
    """Run anyio tests only on the supported asyncio backend."""
    return "asyncio"


class _FakePath:
    """In-memory path stand-in used by the config_fs fixture."""

    def __init__(self, key: str, store: dict[str, str]) -> None:
        self.key = key
        self._store = store

    def exists(self) -> bool:
        return self.key in self._store

    def unlink(self) -> None:
        self._store.pop(self.key, None)

    def chmod(self, mode: int) -> None:
        """No-op in-memory mock for Path.chmod()."""


def _make_fake_open(store: dict[str, str], real_open):  # type: ignore[type-arg]
    """Return an open() replacement that reads/writes into *store*."""

    def fake_open(path_obj, mode: str = "r", encoding: str | None = None):
        if not hasattr(path_obj, "key"):
            return real_open(path_obj, mode=mode, encoding=encoding)

        key = getattr(path_obj, "key", str(path_obj))
        if "r" in mode and key not in store:
            raise FileNotFoundError(key)

        initial = store.get(key, "")
        file_obj = io.StringIO(initial if "r" in mode else "")
        original_close = file_obj.close

        def close_and_save() -> None:
            if any(flag in mode for flag in ("w", "a", "+")):
                store[key] = file_obj.getvalue()
            original_close()

        file_obj.close = close_and_save  # type: ignore[assignment]
        return file_obj

    return fake_open


@pytest.fixture(name="config_fs")
def fixture_config_fs(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Egyszerű in-memory fájlrendszer a konfig tesztekhez."""
    store: dict[str, str] = {}

    monkeypatch.setattr(builtins, "open", _make_fake_open(store, builtins.open))
    monkeypatch.setattr(config, "PROVIDER_PREFS_FILE", _FakePath("prefs", store))
    monkeypatch.setattr(config, "USAGE_TRACKING_FILE", _FakePath("usage", store))
    monkeypatch.setattr(config, "ensure_directories", lambda: None)

    return store
