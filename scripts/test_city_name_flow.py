#!/usr/bin/env python3
"""
Automated GUI test for city_name data flow.

Tests the complete flow from city selection to display in ResultsPanel.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from src.presentation.gui.windows.main_window import MainWindow


class CityNameFlowTest:
    """Automated test for city_name flow."""

    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.window = None
        self.results = []

    def log(self, message):
        """Log test result."""
        print(f"🧪 TEST: {message}")
        self.results.append(message)

    def run_test(self):
        """Run the automated test."""
        print("=" * 80)
        print("🧪 CITY NAME FLOW TEST")
        print("=" * 80)

        # 1. Create MainWindow
        self.log("Creating MainWindow...")
        self.window = MainWindow()
        self.window.show()

        # 2. Wait for initialization
        QTimer.singleShot(2000, self._step_2_select_city)

        # 3. Run event loop
        self.app.exec()

        # 4. Report results
        self._report_results()

    def _step_2_select_city(self):
        """Step 2: Select a city."""
        self.log("Step 2: Selecting city...")

        loc_widget = self.window.control_panel.location_widget
        print(f"   Location widget type: {type(loc_widget)}")
        print(f"   Has signals: {hasattr(loc_widget, 'signals')}")

        if hasattr(loc_widget, 'signals'):
            # Select city
            loc_widget.signals._on_city_selected(
                'Balassagyarmat', 48.07, 19.29, {'country': 'Hungary'}
            )
            self.log("City selected: Balassagyarmat")

            # Check state
            state = loc_widget.get_state()
            city_data = state.get('current_city_data', {})
            print(f"   current_city_data keys: {list(city_data.keys())}")
            print(f"   Has 'name': {'name' in city_data}")
            print(f"   name value: {city_data.get('name')}")

            QTimer.singleShot(1000, self._step_3_trigger_query)
        else:
            self.log("ERROR: Location widget has no signals attribute")
            self.app.quit()

    def _step_3_trigger_query(self):
        """Step 3: Trigger query."""
        self.log("Step 3: Triggering query...")

        # Trigger query
        self.window._on_query_clicked()
        self.log("Query triggered")

        # Wait for results
        QTimer.singleShot(30000, self._step_4_check_results)

    def _step_4_check_results(self):
        """Step 4: Check results."""
        self.log("Step 4: Checking results...")

        # Check if results panel received data
        results_panel = self.window.results_panel
        print(f"   Results panel type: {type(results_panel)}")

        # Check displayed city name
        if hasattr(results_panel, 'current_city_name'):
            city_name = results_panel.current_city_name
            print(f"   ResultsPanel.current_city_name: {city_name}")
            if city_name == 'Balassagyarmat':
                self.log("✅ SUCCESS: City name correctly displayed!")
            else:
                self.log(f"❌ FAIL: Expected 'Balassagyarmat', got '{city_name}'")
        else:
            self.log("WARNING: ResultsPanel has no current_city_name attribute")

        self.app.quit()

    def _report_results(self):
        """Report test results."""
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS")
        print("=" * 80)
        for result in self.results:
            print(f"  {result}")
        print("=" * 80)


if __name__ == "__main__":
    test = CityNameFlowTest()
    test.run_test()
