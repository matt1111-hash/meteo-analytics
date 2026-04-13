#!/usr/bin/env python3
"""
Headless Fetch Flow Integration Test v2 - QEventLoop support

Szimulálja a teljes fetch flow-t GUI indítás nélkül, de QEventLoop-pal.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta

# Qt imports
from PySide6.QtCore import QCoreApplication, QObject, QTimer, Slot
from PySide6.QtWidgets import QApplication

# Import required components
from src.presentation.gui.controller.app_controller import AppController


class TestReceiver(QObject):
    """Signal receiver for testing."""

    def __init__(self):  # noqa: D107
        super().__init__()
        self.signals_received = []
        self.result_data = None

    @Slot(str)
    def on_analysis_started(self, analysis_type: str):  # noqa: D102
        self.signals_received.append(f"analysis_started: {analysis_type}")
        print(f"   📡 SIGNAL: analysis_started - {analysis_type}")

    @Slot(str, int)
    def on_analysis_progress(self, message: str, percentage: int):  # noqa: D102
        self.signals_received.append(f"analysis_progress: {message} ({percentage}%)")
        print(f"   📡 SIGNAL: analysis_progress - {message} ({percentage}%)")

    @Slot(dict)
    def on_analysis_completed(self, result_data: dict):  # noqa: D102
        self.signals_received.append("analysis_completed")
        self.result_data = result_data
        print(f"   📡 SIGNAL: analysis_completed - keys: {list(result_data.keys())}")

        # Quit the event loop when done
        if QCoreApplication.instance():
            QCoreApplication.instance().quit()

    @Slot(str)
    def on_analysis_failed(self, error_message: str):  # noqa: D102
        self.signals_received.append(f"analysis_failed: {error_message}")
        print(f"   ❌ SIGNAL: analysis_failed - {error_message}")

        # Quit the event loop on error
        if QCoreApplication.instance():
            QCoreApplication.instance().quit()


def test_fetch_flow_with_eventloop():  # noqa: PLR0915
    """Test fetch flow with QEventLoop."""
    print("=" * 80)
    print("🧪 HEADLESS FETCH FLOW TEST v2 - QEventLoop")
    print("=" * 80)

    # Create QApplication (required for Qt signals)
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Initialize AppController
    print("\n1️⃣  AppController inicializálás...")
    controller = AppController()
    print("✅ AppController inicializálva")

    # 2. Create signal receiver
    print("\n2️⃣  Signal receiver létrehozása...")
    receiver = TestReceiver()
    print("✅ Signal receiver kész")

    # 3. Connect signals
    print("\n3️⃣  Signal bekötések...")
    controller.analysis_started.connect(receiver.on_analysis_started)
    controller.analysis_progress.connect(receiver.on_analysis_progress)
    controller.analysis_completed.connect(receiver.on_analysis_completed)
    controller.analysis_failed.connect(receiver.on_analysis_failed)
    print("✅ Signalok bekötve")

    # 4. Build test request
    print("\n4️⃣  Analysis request összeállítása...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    test_request = {
        "analysis_type": "single_location",
        "location_data": {
            "name": "Balassagyarmat",
            "latitude": 48.0768832,
            "longitude": 19.2926037,
            "display_name": "Balassagyarmat",
            "country": "Hungary",
        },
        "date_range": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        },
        "api_settings": {
            "cache": False,
            "timeout": 60,
            "timezone": "auto",
        },
        "provider": "open-meteo",
    }
    print(f"   📍 Location: {test_request['location_data']['name']}")
    print(
        f"   📅 Date range: {test_request['date_range']['start_date']} → {test_request['date_range']['end_date']}"
    )

    # 5. Start analysis with timer
    print("\n5️⃣  Analysis indítása timer-rel...")

    def start_analysis():
        try:
            controller.handle_analysis_request(test_request)
            print("✅ Analysis request elküldve")
        except Exception as e:
            print(f"❌ Hiba: {e}")
            import traceback  # noqa: PLC0415

            traceback.print_exc()
            app.quit()

    # Use QTimer to start analysis after event loop starts
    QTimer.singleShot(100, start_analysis)

    # Timeout timer
    def timeout_handler():
        print("⏱️  Timeout (60s) - kilépés")
        if app:
            app.quit()

    QTimer.singleShot(60000, timeout_handler)

    # 6. Run event loop
    print("\n6️⃣  Event loop indítása...")
    print("   (Várakozás signalokra...)")
    app.exec()

    # 7. Report results
    print("\n7️⃣  EREDMÉNYEK:")
    print("=" * 80)

    print(f"\n📡 Fogadott signalok ({len(receiver.signals_received)}):")
    for sig in receiver.signals_received:
        print(f"   - {sig}")

    # Check success
    success = "analysis_completed" in receiver.signals_received

    if success and receiver.result_data:
        print("\n✅ FETCH FLOW SIKERES!")

        # Check result structure
        result_data = receiver.result_data.get("result_data", {})
        if result_data:
            print(f"   📊 Weather data keys: {list(result_data.keys())}")
    else:
        failed = "analysis_failed" in receiver.signals_received
        if failed:
            print("\n❌ FETCH FLOW SIKERTELEN")
        else:
            print("\n⚠️  FETCH FLOW befejezetlen (timeout)")

    # 8. Cleanup
    print("\n8️⃣  Cleanup...")
    controller.shutdown()
    print("✅ Controller leállítva")

    return success


def test_component_imports():
    """Test component imports."""
    print("\n" + "=" * 80)
    print("🔧 KOMPONENS IMPORT TESZT")
    print("=" * 80)

    components = [
        ("ControlPanel", "src.presentation.gui.control_panel"),
        (
            "QueryControlWidget",
            "src.presentation.gui.panel_widgets.query_control_widget",
        ),
        ("LocationWidget", "src.presentation.gui.panel_widgets.location_widget"),
        ("ResultsPanel", "src.presentation.gui.results_panel"),
        ("AppController", "src.presentation.gui.controller.app_controller"),
        ("AnalysisWorker", "src.presentation.gui.workers.analysis_worker"),
    ]

    failed = []
    for name, module_path in components:
        try:
            parts = module_path.split(".")
            __import__(".".join(parts[:-1]), fromlist=[parts[-1]])
            print(f"   ✅ {name}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
            failed.append(name)

    if failed:
        print(f"\n❌ Import hiba: {', '.join(failed)}")
        return False
    else:
        print("\n✅ Összes komponens importálható")
        return True


if __name__ == "__main__":
    # First test imports
    if not test_component_imports():
        sys.exit(1)

    # Then test the fetch flow with event loop
    success = test_fetch_flow_with_eventloop()

    sys.exit(0 if success else 1)
