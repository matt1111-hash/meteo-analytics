"""UsageTracker edge case tesztek."""

from __future__ import annotations

import json
import logging

import pytest

from src import config


def test_track_request_invalid_provider_logs_warning(
    config_fs: dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ismeretlen provider esetén warning log készüljön és a számlálók maradjanak érintetlenek."""
    caplog.set_level(logging.WARNING)

    usage = config.UsageTracker.track_request("storm_api", request_count=2)

    assert usage["total_requests"] == 2
    assert usage["meteostat"]["requests_this_month"] == 0
    assert usage["open_meteo"]["requests_this_month"] == 0

    persisted = json.loads(config_fs["usage"])
    assert persisted["total_requests"] == usage["total_requests"]

    assert "storm_api" in caplog.text
    assert "UsageTracker track_request" in caplog.text
    assert "meteostat" in caplog.text and "open_meteo" in caplog.text
