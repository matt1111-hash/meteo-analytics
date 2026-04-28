"""Tests for atomic JSON write utility and concurrent config access."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import pytest
from src.config.atomic_io import atomic_write_json


class TestAtomicWriteJson:
    """Verify atomic_write_json produces valid files and cleans up on error."""

    def test_writes_valid_json(self, tmp_path: Path) -> None:
        target = tmp_path / "data.json"
        data = {"key": "value", "num": 42}
        atomic_write_json(target, data)

        assert target.exists()
        assert json.loads(target.read_text()) == data

    def test_replaces_existing_content(self, tmp_path: Path) -> None:
        target = tmp_path / "data.json"
        target.write_text('{"old": true}')
        atomic_write_json(target, {"new": True})

        assert json.loads(target.read_text()) == {"new": True}

    def test_no_tmp_file_left_on_success(self, tmp_path: Path) -> None:
        target = tmp_path / "data.json"
        atomic_write_json(target, {"x": 1})

        assert not target.with_suffix(".tmp").exists()

    def test_tmp_file_cleaned_up_on_failure(self, tmp_path: Path) -> None:
        target = tmp_path / "data.json"

        class BadEncoder(json.JSONEncoder):
            def default(self, o: Any) -> Any:
                raise TypeError("forced encode failure")

        with pytest.raises(TypeError):
            atomic_write_json(target, {"bad": object()}, indent=2)

        assert not target.with_suffix(".tmp").exists()

    def test_concurrent_writes_no_corruption(self, tmp_path: Path) -> None:
        """Multiple threads writing to the same file never produce invalid JSON."""
        target = tmp_path / "shared.json"
        target.write_text("{}")
        iterations = 50
        errors: list[Exception] = []

        def writer(thread_id: int) -> None:
            for i in range(iterations):
                try:
                    atomic_write_json(target, {"thread": thread_id, "i": i})
                except Exception as exc:
                    errors.append(exc)

        threads = [threading.Thread(target=writer, args=(tid,)) for tid in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        content = target.read_text()
        parsed = json.loads(content)
        assert "thread" in parsed
        assert "i" in parsed
