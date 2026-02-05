"""Közös pytest fixturek a konfigurációs tesztekhez."""

from __future__ import annotations

import builtins
import io
import json
from typing import Dict

import pytest

from src import config


@pytest.fixture(name="config_fs")
def fixture_config_fs(monkeypatch: pytest.MonkeyPatch) -> Dict[str, str]:
    """Egyszerű in-memory fájlrendszer a konfig tesztekhez."""
    store: Dict[str, str] = {}

    class FakePath:
        def __init__(self, key: str):
            self.key = key

        def exists(self) -> bool:
            return self.key in store

        def unlink(self) -> None:
            if self.key in store:
                del store[self.key]

    real_open = builtins.open

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

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(config, "PROVIDER_PREFS_FILE", FakePath("prefs"))
    monkeypatch.setattr(config, "USAGE_TRACKING_FILE", FakePath("usage"))
    monkeypatch.setattr(config, "ensure_directories", lambda: None)

    return store
