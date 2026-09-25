"""The legacy anomaly API must be importable without eagerly loading its demo."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("demo_first", [False, True])
def test_legacy_api_import_order_in_fresh_interpreter(demo_first: bool) -> None:
    source = """
import importlib
import sys

demo_name = 'src.infrastructure.anomaly.anomaly_demo'
if sys.argv[1] == 'True':
    importlib.import_module(demo_name)
legacy = importlib.import_module('src.infrastructure.anomaly.anomaly_profile_manager')
canonical = importlib.import_module('src.infrastructure.anomaly_profile.manager')
assert legacy.AnomalyProfileManager is canonical.AnomalyProfileManager
assert callable(legacy.demo_anomaly_profile_manager)
if sys.argv[1] == 'False':
    assert demo_name not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", source, str(demo_first)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_legacy_demo_remains_callable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.infrastructure.anomaly.anomaly_profile_manager import (  # noqa: PLC0415
        demo_anomaly_profile_manager,
    )

    monkeypatch.chdir(tmp_path)
    demo_anomaly_profile_manager()

    assert (tmp_path / "demo_data" / "user_preferences").is_dir()
