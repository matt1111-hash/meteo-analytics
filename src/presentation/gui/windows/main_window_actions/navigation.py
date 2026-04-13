# mypy: ignore-errors
"""Navigation and analytics query handling."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities.analytics_models import AnalyticsResult

    from ..windows.main_window import MainWindow


def switch_view(window: "MainWindow", view_name: str) -> None:
    """Nézetváltás a stacked widgetben."""
    view_index_map = {
        "single_city": 0,
        "analytics": 1,
        "trend_analysis": 2,
        "map_view": 3,
        "settings": 4,
    }

    index = view_index_map.get(view_name, 0)
    window.stacked_widget.setCurrentIndex(index)
    window.state.current_view_name = view_name

    if hasattr(window, "view_action_group"):
        action_map = {
            "single_city": window.single_city_action,
            "analytics": window.analytics_action,
            "trend_analysis": window.trend_action,
            "map_view": window.map_action,
            "settings": window.settings_action,
        }
        if view_name in action_map:
            action_map[view_name].setChecked(True)


def map_query_type_to_parameter(query_type: str) -> str:
    """Query type leképezése térképi paraméterre."""
    QUERY_TYPE_TO_PARAMETER = {
        "hottest_today": "Hőmérséklet",
        "coldest_today": "Hőmérséklet",
        "windiest_today": "Szél",
        "wettest_today": "Csapadék",
        "rainiest_today": "Csapadék",
        "sunniest_today": "Hőmérséklet",
        "temperature_range": "Hőmérséklet",
    }
    return QUERY_TYPE_TO_PARAMETER.get(query_type, "Hőmérséklet")


def handle_analytics_view_query(window: "MainWindow", query_type: str, region_name: str) -> None:
    """AnalyticsView multi-city lekérdezés kezelése."""
    params = {"query_type": query_type, "auto_switch_to_map": False}
    today_str = datetime.now().strftime("%Y-%m-%d")

    from .multi_city import handle_multi_city_weather_request  # noqa: PLC0415

    handle_multi_city_weather_request(
        window,
        analysis_type="region",
        region_id=region_name,
        start_date=today_str,
        end_date=today_str,
        params=params,
    )


def handle_multi_city_weather_request(
    window: "MainWindow",
    analysis_type: str,  # noqa: ARG001
    region_id: str,
    start_date: str,
    end_date: str,  # noqa: ARG001
    params: dict,
) -> None:
    """Multi-City weather request kezelése."""
    try:
        query_type = params.get("query_type", "hottest_today")
        limit = params.get("limit", 20)

        if window.hungarian_map_tab:
            display_parameter = map_query_type_to_parameter(query_type)
            if hasattr(window.hungarian_map_tab, "set_analytics_parameter"):
                window.hungarian_map_tab.set_analytics_parameter(display_parameter)

        from src.analytics.ports import get_multi_city_engine_port  # noqa: PLC0415

        engine = get_multi_city_engine_port()
        result = engine.analyze_multi_city(query_type, region_id, start_date, limit=limit)

        if not hasattr(result, "city_results"):
            error_msg = f"Multi-city engine hibás eredmény típus: {type(result)}"
            window.status_bar.showMessage(f"❌ {error_msg}")
            from .dialogs import show_error  # noqa: PLC0415

            show_error(window, error_msg)
            return

        from .multi_city import on_multi_city_result_ready  # noqa: PLC0415

        on_multi_city_result_ready(window, result, query_type)

        success_message = f"✅ Multi-city eredmény: {len(result.city_results)} város ({region_id})"
        window.status_bar.showMessage(success_message)

        if params.get("auto_switch_to_map", True):
            switch_view(window, "map_view")

    except Exception as e:
        from .dialogs import show_error  # noqa: PLC0415

        error_msg = f"Multi-city lekérdezés hiba: {e}"
        window.status_bar.showMessage(f"❌ {error_msg}")
        show_error(window, error_msg)


def on_multi_city_result_ready(
    window: "MainWindow", result: "AnalyticsResult", query_type: str = "hottest_today"
) -> None:
    """Multi-city eredmény szétosztása a nézeteknek."""
    try:
        if window.hungarian_map_tab and hasattr(window.hungarian_map_tab, "set_analytics_result"):
            analytics_parameter = map_query_type_to_parameter(query_type)
            if hasattr(window.hungarian_map_tab, "set_analytics_parameter"):
                window.hungarian_map_tab.set_analytics_parameter(analytics_parameter)
            window.hungarian_map_tab.set_analytics_result(result)

        if window.analytics_panel and hasattr(
            window.analytics_panel, "update_with_multi_city_result"
        ):
            window.analytics_panel.update_with_multi_city_result(result)

    except Exception as e:
        from .dialogs import show_error  # noqa: PLC0415

        show_error(window, f"Multi-city eredmény szétosztási hiba: {e}")
