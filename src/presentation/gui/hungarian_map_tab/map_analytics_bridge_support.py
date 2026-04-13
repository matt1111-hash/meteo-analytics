# mypy: ignore-errors
"""Support helpers for map analytics bridge."""

from __future__ import annotations

from typing import Any


def run_sync_operation(
    bridge: Any,
    sync_type: str,
    completed_signal: str,
    operation: Any,
) -> None:
    """Run a sync operation with shared status and error handling."""
    if bridge.sync_in_progress:
        return
    try:
        bridge.sync_in_progress = True
        bridge._emit_status(sync_type, "in_progress")
        operation()
        bridge._emit_status(sync_type, "success")
        bridge.analytics_sync_completed.emit(completed_signal)
    except Exception as e:
        bridge._emit_status(sync_type, "error")
        bridge.sync_error_occurred.emit(f"{sync_type.capitalize()} sync error: {e}")
    finally:
        bridge.sync_in_progress = False


def apply_analysis_update(bridge: Any, params: dict[str, Any]) -> None:
    """Apply analysis-specific map updates."""
    analysis_type = params.get("analysis_type", "single_location")
    update_actions = {
        "single_location": (
            params.get("location"),
            bridge._update_map_for_single_location,
        ),
        "region": (params.get("region"), bridge._update_map_for_region),
        "county": (params.get("county"), bridge._update_map_for_county),
    }
    target = update_actions.get(analysis_type)
    if target is None:
        return
    value, handler = target
    if value:
        handler(value)


def apply_full_refresh(bridge: Any, analysis: dict, weather: dict, date: dict) -> None:
    """Apply full refresh steps in a consistent order."""
    if analysis:
        apply_analysis_update(bridge, analysis)
    if weather:
        bridge._refresh_weather_overlays(
            weather.get("provider", "auto"), weather.get("cache", True)
        )
    _refresh_temporal_range(bridge, date)


def _refresh_temporal_range(bridge: Any, date: dict) -> None:
    """Refresh temporal map data when full date range is present."""
    if not date:
        return
    start_date = date.get("start_date")
    end_date = date.get("end_date")
    if start_date and end_date:
        bridge._refresh_temporal_data(start_date, end_date)
