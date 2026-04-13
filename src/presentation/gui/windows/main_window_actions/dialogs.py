# mypy: ignore-errors
"""Dialogs and cleanup functions."""

import contextlib
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from ..windows.main_window import MainWindow


def handle_export_request(window: "MainWindow", format: str) -> None:
    """Export request kezelése."""
    try:
        from ..data_widgets import WeatherDataTable  # noqa: PLC0415

        if window.results_panel and hasattr(window.results_panel, "data_table"):
            data_table: WeatherDataTable = window.results_panel.data_table

            if data_table and hasattr(data_table, "export_data"):
                data_table.export_data(format)
            else:
                show_error(window, "Nincs exportálható adat.")
        else:
            show_error(window, "Nincs megjelenített eredmény az exportáláshoz.")
    except Exception as e:
        show_error(window, f"Export hiba: {e}")


def show_extreme_weather(window: "MainWindow") -> None:
    """Szélsőséges időjárás dialog."""
    try:
        from ..dialogs import ExtremeWeatherDialog  # noqa: PLC0415

        dialog = ExtremeWeatherDialog(window)
        dialog.exec()
    except Exception as e:
        show_error(window, f"Hiba a szélsőséges időjárás megnyitásakor: {e}")


def show_about(window: "MainWindow") -> None:
    """Névjegy dialog."""
    from src.config import AppInfo  # noqa: PLC0415

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
        """,
    )


def show_error(window: "MainWindow", message: str) -> None:
    """Hibaüzenet megjelenítése."""
    QMessageBox.critical(window, "Hiba", message)


# === Thread Cleanup ===


def register_thread(window: "MainWindow", thread: QThread) -> None:
    """Thread regisztrálása cleanup-hoz."""
    window.state.register_thread(thread)


def register_worker(window: "MainWindow", worker) -> None:
    """Worker regisztrálása cleanup-hoz."""
    window.state.register_worker(worker)


def register_web_view(window: "MainWindow", web_view: QWebEngineView) -> None:
    """WebEngine view regisztrálása cleanup-hoz."""
    window.state.register_web_view(web_view)


def register_timer(window: "MainWindow", timer: QTimer) -> None:
    """QTimer regisztrálása cleanup-hoz."""
    window.state.register_timer(timer)


def cleanup_all_threads(window: "MainWindow") -> None:
    """Minden thread cleanup."""
    for thread in window.state.active_threads:
        if thread.isRunning():
            thread.quit()
            thread.wait()


def cleanup_all_workers(window: "MainWindow") -> None:
    """Minden worker cleanup."""
    for worker in window.state.active_workers:
        if hasattr(worker, "stop"):
            worker.stop()
        if hasattr(worker, "quit"):
            worker.quit()
        if hasattr(worker, "wait"):
            worker.wait()


def cleanup_all_web_engines(window: "MainWindow") -> None:
    """Minden WebEngine cleanup."""
    for web_view in window.state.web_engine_views:
        with contextlib.suppress(Exception):
            web_view.close()


def cleanup_all_timers(window: "MainWindow") -> None:
    """Minden QTimer cleanup."""
    for timer in window.state.cleanup_timers:
        timer.stop()
