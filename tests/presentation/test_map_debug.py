"""Exercise the retained map-debug facade against its actual helper module."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from src.presentation.gui.map.map_visualizer import debug


@pytest.fixture
def visualizer(tmp_path: Path) -> SimpleNamespace:
    map_file = tmp_path / "map.html"
    map_file.write_text("map", encoding="utf-8")
    return SimpleNamespace(
        local_server=SimpleNamespace(running=True),
        http_host="127.0.0.1",
        http_port=8123,
        current_map_file=str(map_file),
        counties_gdf=["Pest"],
        current_weather_data={"temperature": {}},
        get_active_overlay_parameter=lambda: "temperature",
    )


def test_generate_demo_weather_data(visualizer: SimpleNamespace) -> None:
    data = debug.generate_demo_weather_data(visualizer)
    assert set(data) == {"temperature", "precipitation", "wind_speed"}
    assert data["temperature"]["Budapest"]["coordinates"] == [47.4979, 19.0402]


def test_get_http_server_info(visualizer: SimpleNamespace) -> None:
    info = debug.get_http_server_info(visualizer)
    assert info["server_running"] is True
    assert info["server_url"] == "http://127.0.0.1:8123"
    assert info["current_map_size"] == 3


def test_get_dynamic_gradient_info(visualizer: SimpleNamespace) -> None:
    info = debug.get_dynamic_gradient_info(visualizer)
    assert info["active_overlay_parameter"] == "temperature"
    assert info["dynamic_gradient_support"] is True
    assert info["gradient_mapping"]


def test_get_http_debug_info(visualizer: SimpleNamespace) -> None:
    info = debug.get_http_debug_info(visualizer)
    assert info["http_server_running"] is True
    assert info["counties_count"] == 1
    assert info["weather_data_loaded"] is True
    assert info["map_file_size"] == 3
