#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window Actions - Akciókezelők a MainWindow számára.

FÁJL: src/presentation/gui/windows/main_window_actions.py
"""

from typing import TYPE_CHECKING, Optional
from datetime import datetime

from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView

if TYPE_CHECKING:
    from .main_window import MainWindow


def switch_view(window: 'MainWindow', view_name: str) -> None:
    """
    🔄 Nézetváltás a stacked widgetben.

    Args:
        window: MainWindow példány
        view_name: Nézet neve (single_city, analytics, trend_analysis, map_view, settings)
    """
    view_index_map = {
        "single_city": 0,
        "analytics": 1,
        "trend_analysis": 2,
        "map_view": 3,
        "settings": 4
    }

    index = view_index_map.get(view_name, 0)
    window.stacked_widget.setCurrentIndex(index)
    window.state.current_view_name = view_name

    # Toolbar action frissítése
    if hasattr(window, 'view_action_group'):
        action_map = {
            "single_city": window.single_city_action,
            "analytics": window.analytics_action,
            "trend_analysis": window.trend_action,
            "map_view": window.map_action,
            "settings": window.settings_action
        }
        if view_name in action_map:
            action_map[view_name].setChecked(True)


def handle_analytics_view_query(window: 'MainWindow', query_type: str, region_name: str) -> None:
    """
    🚨 Kezeli az AnalyticsView-ből érkező multi-city lekérdezési kéréseket.

    Args:
        window: MainWindow példány
        query_type: Lekérdezés típusa
        region_name: Régió neve
    """
    params = {
        "query_type": query_type,
        "auto_switch_to_map": False
    }

    today_str = datetime.now().strftime("%Y-%m-%d")

    handle_multi_city_weather_request(
        window,
        analysis_type="region",
        region_id=region_name,
        start_date=today_str,
        end_date=today_str,
        params=params
    )


def handle_multi_city_weather_request(
    window: 'MainWindow',
    analysis_type: str,
    region_id: str,
    start_date: str,
    end_date: str,
    params: dict
) -> None:
    """
    🎉 Multi-City weather request kezelése.

    Args:
        window: MainWindow példány
        analysis_type: Elemzés típusa
        region_id: Régió azonosító
        start_date: Kezdő dátum
        end_date: Vég dátum
        params: További paraméterek
    """
    try:
        query_type = params.get("query_type", "hottest_today")
        limit = params.get("limit", 20)

        # 1. Paraméter beállítás a térképen
        if window.hungarian_map_tab:
            display_parameter = map_query_type_to_parameter(query_type)
            if hasattr(window.hungarian_map_tab, 'set_analytics_parameter'):
                window.hungarian_map_tab.set_analytics_parameter(display_parameter)

        # 2. Multi-City elemzés
        from src.analytics.multi_city_engine import MultiCityEngine
        engine = MultiCityEngine()
        result = engine.analyze_multi_city(query_type, region_id, start_date, limit=limit)

        if not hasattr(result, 'city_results'):
            error_msg = f"Multi-city engine hibás eredmény típus: {type(result)}"
            window.status_bar.showMessage(f"❌ {error_msg}")
            show_error(window, error_msg)
            return

        # 3. Eredmény szétosztása a nézeteknek
        on_multi_city_result_ready(window, result, query_type)

        # 4. Status update
        success_message = f"✅ Multi-city eredmény: {len(result.city_results)} város ({region_id})"
        window.status_bar.showMessage(success_message)

        if params.get("auto_switch_to_map", True):
            switch_view(window, "map_view")

    except Exception as e:
        error_msg = f"Multi-city lekérdezés hiba: {e}"
        window.status_bar.showMessage(f"❌ {error_msg}")
        show_error(window, error_msg)


def on_multi_city_result_ready(window: 'MainWindow', result: 'AnalyticsResult', query_type: str = "hottest_today") -> None:
    """
    🔥 Szétosztja a multi-city elemzés eredményét a nézeteknek.

    Args:
        window: MainWindow példány
        result: AnalyticsResult objektum
        query_type: Lekérdezés típusa
    """
    try:
        # Térképnek
        if window.hungarian_map_tab and hasattr(window.hungarian_map_tab, 'set_analytics_result'):
            analytics_parameter = map_query_type_to_parameter(query_type)
            if hasattr(window.hungarian_map_tab, 'set_analytics_parameter'):
                window.hungarian_map_tab.set_analytics_parameter(analytics_parameter)
            window.hungarian_map_tab.set_analytics_result(result)

        # Analytics nézetnek
        if window.analytics_panel and hasattr(window.analytics_panel, 'update_with_multi_city_result'):
            window.analytics_panel.update_with_multi_city_result(result)

    except Exception as e:
        show_error(window, f"Multi-city eredmény szétosztási hiba: {e}")


def map_query_type_to_parameter(query_type: str) -> str:
    """
    🔧 Query type leképezése térképi paraméterre.

    Args:
        query_type: Analytics query type

    Returns:
        Térkép paraméter neve
    """
    QUERY_TYPE_TO_PARAMETER = {
        "hottest_today": "Hőmérséklet",
        "coldest_today": "Hőmérséklet",
        "windiest_today": "Szél",
        "wettest_today": "Csapadék",
        "rainiest_today": "Csapadék",
        "sunniest_today": "Hőmérséklet",
        "temperature_range": "Hőmérséklet"
    }
    return QUERY_TYPE_TO_PARAMETER.get(query_type, "Hőmérséklet")


def handle_export_request(window: 'MainWindow', format: str) -> None:
    """
    📤 Export request kezelése.

    Args:
        window: MainWindow példány
        format: Export formátum
    """
    try:
        from ..data_widgets import WeatherDataTable
        from ..utils import format_provider_status

        if window.results_panel and hasattr(window.results_panel, 'data_table'):
            data_table: WeatherDataTable = window.results_panel.data_table

            if data_table and hasattr(data_table, 'export_data'):
                data_table.export_data(format)
            else:
                show_error(window, "Nincs exportálható adat.")
        else:
            show_error(window, "Nincs megjelenített eredmény az exportáláshoz.")
    except Exception as e:
        show_error(window, f"Export hiba: {e}")


def show_extreme_weather(window: 'MainWindow') -> None:
    """
    🌪️ Szélsőséges időjárás dialog megjelenítése.

    Args:
        window: MainWindow példány
    """
    try:
        from ..dialogs import ExtremeWeatherDialog
        dialog = ExtremeWeatherDialog(window)
        dialog.exec()
    except Exception as e:
        show_error(window, f"Hiba a szélsőséges időjárás megnyitásakor: {e}")


def show_about(window: 'MainWindow') -> None:
    """
    ℹ️ Névjegy dialog megjelenítése.

    Args:
        window: MainWindow példány
    """
    from ..config import AppInfo

    QMessageBox.about(
        window,
        f"Névjegy - {AppInfo.NAME}",
        f"""
        <h2>{AppInfo.NAME}</h2>
        <p><b>Verzió:</b> {AppInfo.VERSION}</p>
        <p><b>Leírás:</b> {AppInfo.DESCRIPTION}</p>
        <p><b>Szerző:</b> {AppInfo.AUTHOR}</p>
        <hr>
        <p>Egyetemes időjárási kutatási platform</p>
        <p>Multi-city analytics, térképes megjelenítés, trend elemzés</p>
        """
    )


def show_error(window: 'MainWindow', message: str) -> None:
    """
    ❌ Hibaüzenet megjelenítése.

    Args:
        window: MainWindow példány
        message: Hibaüzenet
    """
    QMessageBox.critical(window, "Hiba", message)


# === Thread Cleanup ===

def register_thread(window: 'MainWindow', thread: QThread) -> None:
    """Thread regisztrálása cleanup-hoz."""
    window.state.register_thread(thread)


def register_worker(window: 'MainWindow', worker) -> None:
    """Worker regisztrálása cleanup-hoz."""
    window.state.register_worker(worker)


def register_web_view(window: 'MainWindow', web_view: QWebEngineView) -> None:
    """WebEngine view regisztrálása cleanup-hoz."""
    window.state.register_web_view(web_view)


def register_timer(window: 'MainWindow', timer: QTimer) -> None:
    """QTimer regisztrálása cleanup-hoz."""
    window.state.register_timer(timer)


def cleanup_all_threads(window: 'MainWindow') -> None:
    """Minden thread cleanup."""
    for thread in window.state.active_threads:
        if thread.isRunning():
            thread.quit()
            thread.wait()


def cleanup_all_workers(window: 'MainWindow') -> None:
    """Minden worker cleanup."""
    for worker in window.state.active_workers:
        if hasattr(worker, 'stop'):
            worker.stop()
        if hasattr(worker, 'quit'):
            worker.quit()
        if hasattr(worker, 'wait'):
            worker.wait()


def cleanup_all_web_engines(window: 'MainWindow') -> None:
    """Minden WebEngine cleanup."""
    for web_view in window.state.web_engine_views:
        try:
            web_view.close()
        except Exception:
            pass


def cleanup_all_timers(window: 'MainWindow') -> None:
    """Minden QTimer cleanup."""
    for timer in window.state.cleanup_timers:
        timer.stop()


# Export
__all__ = [
    'switch_view',
    'handle_analytics_view_query',
    'handle_multi_city_weather_request',
    'on_multi_city_result_ready',
    'map_query_type_to_parameter',
    'handle_export_request',
    'show_extreme_weather',
    'show_about',
    'show_error',
    'register_thread',
    'register_worker',
    'register_web_view',
    'register_timer',
    'cleanup_all_threads',
    'cleanup_all_workers',
    'cleanup_all_web_engines',
    'cleanup_all_timers',
]
