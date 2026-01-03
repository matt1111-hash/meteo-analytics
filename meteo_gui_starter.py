#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Main Application Entry Point (MVC Refactored)
Főalkalmazás belépési pont - MVC architektúrával.

Ez a modul tartalmazza a Global Weather Analyzer alkalmazás fő belépési pontját.
Az új MVC architektúra miatt jelentősen egyszerűsödött.

Refaktorált architektúra:
- AppController központi logika
- MainWindow komponens koordináció
- Moduláris design, thread pool management
"""

import signal
import sys
import traceback
from pathlib import Path
from typing import Optional

# PySide6 import with error handling
try:
    from PySide6.QtCore import Qt  # noqa: F401
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QMessageBox
except ImportError as e:
    print("❌ PySide6 import hiba!")
    print("Telepítse a szükséges függőségeket:")
    print("pip install -r requirements-base.txt")
    print(f"Részletes hiba: {e}")
    sys.exit(1)

# Project imports
try:
    from src.config import AppInfo, ensure_directories
    from src.gui.main_window import MainWindow
except ImportError as e:
    print("❌ Modul import hiba!")
    print("Ellenőrizze a projekt struktúrát és a PYTHONPATH-t.")
    print(f"Részletes hiba: {e}")
    sys.exit(1)


class WeatherAnalyzerApp:
    """
    Global Weather Analyzer egyszerűsített alkalmazás osztály.

    Az új MVC architektúra miatt jelentősen egyszerűsödött:
    - A MainWindow kezeli a komponens koordinációt
    - Az AppController kezeli az üzleti logikát
    - Ez az osztály csak a minimális bootstrap funkciókat tartalmazza
    """

    def __init__(self):
        """Alkalmazás inicializálása."""
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None

        # Signal handlers beállítása
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """System signal handlers beállítása."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame) -> None:
        """System signal kezelő."""
        print(f"\n🛑 Signal {signum} fogadva. Alkalmazás leállítása...")
        self.shutdown()

    def initialize(self) -> bool:
        """
        Alkalmazás inicializálása.

        Returns:
            Sikeres inicializálás-e
        """
        try:
            print("🚀 Global Weather Analyzer indítása (MVC architektúra)...")

            # === QAPPLICATION LÉTREHOZÁSA ===

            self.app = QApplication(sys.argv)
            self.app.setApplicationName(AppInfo.NAME)
            self.app.setApplicationVersion(AppInfo.VERSION)
            self.app.setOrganizationName("Weather Analytics")

            # === ALKALMAZÁS IKON ===

            self._set_application_icon()

            # === KÖNYVTÁRAK BIZTOSÍTÁSA ===

            ensure_directories()
            print("✅ Projekt könyvtárak ellenőrizve")

            # === FŐ ABLAK LÉTREHOZÁSA ===

            # Az új MVC architektúrában a MainWindow maga kezeli:
            # - AppController létrehozását
            # - Komponensek inicializálását
            # - Signal-slot összekötéseket
            # - Worker management-et

            self.main_window = MainWindow()
            print("✅ MainWindow létrehozva (MVC komponensekkel)")

            print("✅ Alkalmazás sikeresen inicializálva!")
            return True

        except Exception as e:
            print(f"❌ Inicializálási hiba: {e}")
            traceback.print_exc()
            self._show_error("Inicializálási hiba", str(e))
            return False

    def _set_application_icon(self) -> None:
        """Alkalmazás ikon beállítása."""
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.png"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
            else:
                print("ℹ️ Alkalmazás ikon nem található (nem kritikus)")
        except Exception as e:
            print(f"⚠️ Ikon beállítási hiba: {e}")

    def run(self) -> int:
        """
        Alkalmazás futtatása.

        Returns:
            Alkalmazás exit kódja
        """
        try:
            if not self.initialize():
                return 1

            # === FŐ ABLAK MEGJELENÍTÉSE ===

            self.main_window.show()

            print("🎉 Alkalmazás sikeresen elindult!")
            print("📍 Válasszon települést az időjárási adatok lekérdezéséhez.")
            print("🏗️ MVC Architektúra:")
            print("   📋 AppController - Üzleti logika")
            print("   🖼️  MainWindow - UI koordináció")
            print("   🎛️  ControlPanel - Bemenet kezelés")
            print("   📊 ResultsPanel - Eredmények megjelenítés")

            # === EVENT LOOP INDÍTÁSA ===

            return self.app.exec()

        except KeyboardInterrupt:
            print("\n⚠️ Felhasználó megszakította az alkalmazást")
            return 0
        except Exception as e:
            print(f"❌ Runtime hiba: {e}")
            traceback.print_exc()
            self._show_error("Runtime hiba", str(e))
            return 1

    def shutdown(self) -> None:
        """Alkalmazás graceful leállítása."""
        try:
            print("🛑 Alkalmazás leállítása...")

            # === MAIN WINDOW BEZÁRÁSA ===

            # A MainWindow closeEvent metódusa automatikusan:
            # - Elmenti a beállításokat
            # - Leállítja az AppController-t
            # - Az AppController leállítja a Worker-eket

            if self.main_window:
                self.main_window.close()
                print("✅ MainWindow bezárva")

            # === QAPPLICATION LEÁLLÍTÁSA ===

            if self.app:
                self.app.quit()
                print("✅ QApplication leállítva")

        except Exception as e:
            print(f"⚠️ Leállítási hiba: {e}")

    def _show_error(self, title: str, message: str) -> None:
        """Hibaüzenet megjelenítése."""
        if self.app:
            QMessageBox.critical(None, title, message)
        else:
            print(f"❌ {title}: {message}")


def check_requirements() -> bool:
    """
    Alapvető követelmények ellenőrzése.

    Returns:
        Megfelelnek-e a követelmények
    """
    # === PYTHON VERZIÓ ===

    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ szükséges!")
        print(f"Jelenlegi verzió: {sys.version}")
        return False

    # === PROJEKT STRUKTÚRA ===

    project_root = Path(__file__).parent

    # ✅ JAVÍTOTT: Moduláris results_panel struktúra ellenőrzése
    required_paths = [
        project_root / "src",
        project_root / "src" / "gui",
        project_root / "src" / "config.py",
        project_root / "src" / "gui" / "main_window.py",
        project_root / "src" / "gui" / "app_controller.py",
        project_root / "src" / "gui" / "control_panel.py",
        # ✅ JAVÍTOTT: Moduláris results_panel mappa és fájlok ellenőrzése
        project_root / "src" / "gui" / "results_panel",
        project_root / "src" / "gui" / "results_panel" / "__init__.py",
        project_root / "src" / "gui" / "results_panel" / "results_panel.py",
        project_root / "src" / "gui" / "results_panel" / "quick_overview_tab.py",
        project_root / "src" / "gui" / "results_panel" / "detailed_charts_tab.py",
        project_root / "src" / "gui" / "results_panel" / "data_table_tab.py",
        project_root / "src" / "gui" / "results_panel" / "extreme_events_tab.py",
        project_root / "src" / "gui" / "results_panel" / "utils.py"
    ]

    missing_files = []
    for path in required_paths:
        if not path.exists():
            missing_files.append(str(path))

    if missing_files:
        print("❌ Hiányzó fájlok:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    # === MODULÁRIS RESULTS PANEL VALIDÁCIÓ ===

    try:
        # ✅ JAVÍTOTT: Results panel moduláris import teszt
        from src.gui.results_panel import QuickOverviewTab, ResultsPanel  # noqa: F401
        print("✅ Results panel moduláris architektúra: OK")

    except ImportError as e:
        print(f"❌ Results panel import hiba: {e}")
        print("A moduláris results_panel struktúra hibás!")
        return False

    # === REQUIREMENTS ELLENŐRZÉSE ===

    try:
        # PySide6 ellenőrzése
        import PySide6
        print(f"✅ PySide6 verzió: {PySide6.__version__}")

        # httpx ellenőrzése
        import httpx
        print(f"✅ httpx verzió: {httpx.__version__}")

        # pandas ellenőrzése
        import pandas
        print(f"✅ pandas verzió: {pandas.__version__}")

        # matplotlib ellenőrzése
        import matplotlib
        print(f"✅ matplotlib verzió: {matplotlib.__version__}")

    except ImportError as e:
        print(f"❌ Hiányzó függőség: {e}")
        print("Telepítse a hiányzó csomagokat:")
        print("pip install -r requirements-base.txt")
        return False

    return True


def main() -> int:
    """
    Fő belépési pont.

    Returns:
        Exit kód
    """
    print("=" * 70)
    print(f"  {AppInfo.NAME}")
    print(f"  Verzió: {AppInfo.VERSION}")
    print("  Meteorológiai adatelemző alkalmazás")
    print("  Architektúra: MVC (Model-View-Controller)")
    print("=" * 70)

    # === KÖVETELMÉNYEK ELLENŐRZÉSE ===

    print("\n🔍 Követelmények ellenőrzése...")

    if not check_requirements():
        print("\n❌ A követelmények nem teljesülnek!")
        print("Telepítse a hiányzó függőségeket:")
        print("pip install -r requirements-base.txt")
        return 1

    print("✅ Minden követelmény teljesül!")

    # === ALKALMAZÁS PÉLDÁNY LÉTREHOZÁSA ÉS FUTTATÁSA ===

    weather_app = WeatherAnalyzerApp()

    try:
        return weather_app.run()

    except KeyboardInterrupt:
        print("\n⚠️ Alkalmazás megszakítva (Ctrl+C)")
        weather_app.shutdown()
        return 0

    except Exception as e:
        print(f"\n❌ Váratlan hiba: {e}")
        traceback.print_exc()
        weather_app.shutdown()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n👋 Alkalmazás leállt (exit code: {exit_code})")
    sys.exit(exit_code)
