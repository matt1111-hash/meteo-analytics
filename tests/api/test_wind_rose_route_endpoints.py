"""Tests for the wind rose API route."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from src.api.routes import wind_rose


@pytest.mark.asyncio
async def test_get_wind_rose_reconstructs_daily_data_from_flat_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The route should rebuild daily payloads from flat weather records."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(return_value=MagicMock(find_city_by_name=MagicMock(return_value=(47.5, 19.0)))),
    )
    monkeypatch.setattr(
        wind_rose,
        "WeatherClient",
        MagicMock(
            return_value=MagicMock(
                get_weather_data=MagicMock(
                    return_value=[
                        {
                            "date": "2026-03-01",
                            "winddirection_10m_dominant": 0.0,
                            "wind_gusts_10m_max": 10.0,
                        },
                        {
                            "date": "2026-03-02",
                            "winddirection_10m_dominant": 90.0,
                            "wind_gusts_10m_max": 30.0,
                        },
                    ]
                )
            )
        ),
    )
    request = wind_rose.WindRoseRequest(
        city="Budapest",
        start="2026-03-01",
        end="2026-03-02",
    )

    response = await wind_rose.get_wind_rose(request)

    assert response.city == "Budapest"
    assert response.total_observations == 2
    assert response.statistics["data_source"] == "wind_gusts_max"


@pytest.mark.asyncio
async def test_get_wind_rose_uses_embedded_daily_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The route should accept records that already contain a daily payload."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(return_value=MagicMock(find_city_by_name=MagicMock(return_value=(47.5, 19.0)))),
    )
    monkeypatch.setattr(
        wind_rose,
        "WeatherClient",
        MagicMock(
            return_value=MagicMock(
                get_weather_data=MagicMock(
                    return_value=[
                        {
                            "daily": {
                                "time": ["2026-03-01"],
                                "winddirection_10m_dominant": [45.0],
                                "windspeed_10m_max": [15.0],
                            }
                        }
                    ]
                )
            )
        ),
    )

    response = await wind_rose.get_wind_rose(
        wind_rose.WindRoseRequest(city="Budapest", start="2026-03-01", end="2026-03-01")
    )

    assert response.total_observations == 1
    assert response.statistics["data_source"] == "windspeed_10m_max"


@pytest.mark.asyncio
async def test_get_wind_rose_returns_404_for_unknown_city(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The route should map missing cities to HTTP 404."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(return_value=MagicMock(find_city_by_name=MagicMock(return_value=None))),
    )
    request = wind_rose.WindRoseRequest(
        city="Unknown",
        start="2026-03-01",
        end="2026-03-02",
    )

    with pytest.raises(HTTPException, match="City not found: Unknown") as exc_info:
        await wind_rose.get_wind_rose(request)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_wind_rose_returns_404_for_missing_weather_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing weather rows should map to HTTP 404."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(return_value=MagicMock(find_city_by_name=MagicMock(return_value=(47.5, 19.0)))),
    )
    monkeypatch.setattr(
        wind_rose,
        "WeatherClient",
        MagicMock(return_value=MagicMock(get_weather_data=MagicMock(return_value=[]))),
    )

    with pytest.raises(HTTPException, match="No weather data found") as exc_info:
        await wind_rose.get_wind_rose(
            wind_rose.WindRoseRequest(city="Budapest", start="2026-03-01", end="2026-03-02")
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_wind_rose_returns_400_when_no_daily_weather_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Records without usable daily wind fields should return HTTP 400."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(return_value=MagicMock(find_city_by_name=MagicMock(return_value=(47.5, 19.0)))),
    )
    monkeypatch.setattr(
        wind_rose,
        "WeatherClient",
        MagicMock(
            return_value=MagicMock(
                get_weather_data=MagicMock(return_value=[{"date": "2026-03-01"}])
            )
        ),
    )

    with pytest.raises(HTTPException, match="No daily weather data available") as exc_info:
        await wind_rose.get_wind_rose(
            wind_rose.WindRoseRequest(city="Budapest", start="2026-03-01", end="2026-03-02")
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_wind_rose_maps_value_error_to_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Value errors from collaborators should map to HTTP 400."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(
            return_value=MagicMock(find_city_by_name=MagicMock(side_effect=ValueError("bad city")))
        ),
    )

    with pytest.raises(HTTPException, match="bad city") as exc_info:
        await wind_rose.get_wind_rose(
            wind_rose.WindRoseRequest(city="Budapest", start="2026-03-01", end="2026-03-02")
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_wind_rose_maps_unexpected_error_to_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected errors should be converted to HTTP 500."""
    monkeypatch.setattr(
        wind_rose,
        "get_city_manager_port",
        MagicMock(return_value=MagicMock(find_city_by_name=MagicMock(return_value=(47.5, 19.0)))),
    )
    monkeypatch.setattr(
        wind_rose,
        "WeatherClient",
        MagicMock(
            return_value=MagicMock(get_weather_data=MagicMock(side_effect=RuntimeError("boom")))
        ),
    )

    with pytest.raises(HTTPException, match="Internal server error") as exc_info:
        await wind_rose.get_wind_rose(
            wind_rose.WindRoseRequest(city="Budapest", start="2026-03-01", end="2026-03-02")
        )

    assert exc_info.value.status_code == 500
