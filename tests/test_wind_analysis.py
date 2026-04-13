import datetime as dt

import pytest

pd = pytest.importorskip("pandas")

from src.analytics import wind_analysis as wa  # noqa: E402


def test_extract_daily_wind_data_prefers_gusts_and_filters_invalid_values():
    weather = pd.DataFrame(
        {
            "date": [
                "2024-01-01 00:00",
                "2024-01-01 12:00",
                "2024-01-02 06:00",
                "2024-01-02 09:00",
                "2024-01-02 12:00",
            ],
            "wind_gusts_max": [40.0, 60.0, 55.0, None, -5.0],
            "wind_speed": [20.0, 30.0, 25.0, 15.0, 10.0],
            "windspeed_10m_max": [15.0] * 5,
        }
    )

    result = wa.extract_daily_wind_data(weather)
    result = result.sort_values("date").reset_index(drop=True)

    assert list(result["date"]) == [dt.date(2024, 1, 1), dt.date(2024, 1, 2)]
    assert list(result["max_wind_speed_kmh"]) == [60.0, 55.0]


def test_extract_daily_wind_data_falls_back_to_wind_speed_when_gusts_missing():
    weather = pd.DataFrame(
        {
            "date": ["2024-03-01 00:00", "2024-03-02 00:00"],
            "wind_speed": [30.0, 45.0],
        }
    )

    result = wa.extract_daily_wind_data(weather)
    result = result.sort_values("date").reset_index(drop=True)

    assert list(result["max_wind_speed_kmh"]) == [30.0, 45.0]


def test_calculate_monthly_windy_stats_inserts_missing_months():
    windy_days = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-15", "2024-03-10"]),
            "max_wind_speed_kmh": [55.0, 20.0],
            "is_windy": [True, False],
        }
    )

    stats = wa.calculate_monthly_windy_stats(windy_days)
    stats_by_month = {(entry.year, entry.month): entry for entry in stats}

    assert (2024, 2) in stats_by_month  # February inserted with zeros
    feb = stats_by_month[(2024, 2)]
    assert feb.windy_days_count == 0
    assert feb.total_days == 0
    assert feb.max_wind_speed == 0.0


def test_analyze_wind_patterns_computes_summary_across_months():
    weather = pd.DataFrame(
        {
            "date": [
                "2024-01-01 00:00",
                "2024-01-02 00:00",
                "2024-02-01 00:00",
            ],
            "wind_gusts_max": [60.0, 48.0, 25.0],
            "wind_speed": [20.0, 25.0, 15.0],
        }
    )

    analysis = wa.analyze_wind_patterns(weather, location_name="Budapest", threshold_kmh=45.0)

    assert analysis.location_name == "Budapest"
    assert analysis.total_days == 3
    assert analysis.total_windy_days == 2
    assert analysis.windiest_month.month == 1
    assert analysis.calmest_month.month == 2
    assert analysis.overall_windy_percentage == pytest.approx(66.666, rel=1e-3)
    assert analysis.analysis_period == (dt.date(2024, 1, 1), dt.date(2024, 2, 1))
