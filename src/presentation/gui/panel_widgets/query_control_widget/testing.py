"""
Testing support for QueryControlWidget.

Ez a modul tartalmazza a QueryControlWidget tesztelési támogatását.
"""

import logging
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class QueryControlTestWindow(QMainWindow):
    """Test window a QueryControlWidgethez."""

    def __init__(self, query_widget):
        super().__init__()
        self.setWindowTitle("QueryControlWidget Test - Validation Fix")
        self.setGeometry(100, 100, 400, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Test controls
        controls_layout = QHBoxLayout()

        test_validation_btn = QPushButton("🔍 Test Validation")
        test_validation_btn.clicked.connect(self._test_validation)
        controls_layout.addWidget(test_validation_btn)

        test_fetch_btn = QPushButton("📄 Test Fetch")
        test_fetch_btn.clicked.connect(self._test_fetch)
        controls_layout.addWidget(test_fetch_btn)

        test_error_btn = QPushButton("❌ Test Error")
        test_error_btn.clicked.connect(self._test_error)
        controls_layout.addWidget(test_error_btn)

        layout.addLayout(controls_layout)

        # Query control widget
        self.query_widget = query_widget
        self.query_widget.query_requested.connect(self._on_query_requested)
        self.query_widget.cancel_requested.connect(self._on_cancel_requested)
        layout.addWidget(self.query_widget)

        # Test timer
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self._simulate_fetch_complete)

    def _test_validation(self):
        """Validáció tesztelése."""
        print("🔍 TEST: Testing validation logic")
        is_valid = self.query_widget.is_fetching
        print(f"   Fetching state: {is_valid}")

    def _test_fetch(self):
        """Fetch tesztelése."""
        print("📄 TEST: Simulating fetch start")
        self.query_widget.set_fetching_state(True, "🧪 Test fetch in progress...")
        self.test_timer.start(3000)  # 3 seconds

    def _test_error(self):
        """Error tesztelése."""
        print("❌ TEST: Simulating error")
        self.query_widget.set_error_state("Test error message")

    def _simulate_fetch_complete(self):
        """Fetch befejezésének szimulálása."""
        print("✅ TEST: Simulating fetch complete")
        self.test_timer.stop()
        self.query_widget.set_fetching_state(False)

    def _on_query_requested(self, params):
        """Query kérés kezelése."""
        print(f"🚀 TEST: Query requested with params: {params}")
        self._test_fetch()

    def _on_cancel_requested(self):
        """Cancel kérés kezelése."""
        print("🚫 TEST: Cancel requested")
        self.test_timer.stop()
        self.query_widget.force_reset()


def run_standalone_test():
    """Standalone teszt futtatása."""
    from .core import QueryControlWidget

    app = QApplication(sys.argv)
    query_widget = QueryControlWidget()
    window = QueryControlTestWindow(query_widget)
    window.show()

    print("🧪 DEBUG: QueryControlWidget test window started")
    print("🎯 TEST: Próbáld ki a validation fix funkciókat!")

    sys.exit(app.exec())
