#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Base Worker Thread - Base class for all worker threads

Teljes cancellation support-tal rendelkező base osztály
minden worker thread számára.
"""

from typing import Optional

from PySide6.QtCore import QObject, QThread, QTimer, Signal


class BaseWorkerThread(QThread):
    """
    🔧 CRITICAL FIX: Base worker thread class teljes cancellation support-tal.

    ÚJ FUNKCIÓK:
    ✅ Explicit completion_signal minden esetben
    ✅ Comprehensive cancellation support
    ✅ Periodic interruption checks
    ✅ Proper thread lifecycle management
    ✅ Progress tracking standardizálva
    """

    # 🚨 FIX: Teljes signal set minden worker-hez
    finished = Signal()
    completion_signal = Signal()  # ← ÚJ: Explicit completion jelzés UI-nak
    error_occurred = Signal(str)
    progress_updated = Signal(int)  # 0-100 százalék
    cancellation_requested = Signal()  # ← ÚJ: Cancel signal internal tracking
    status_updated = Signal(str)  # ← ÚJ: Status message updates

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.is_cancelled = False
        self._error_message = ""
        self._status_message = ""

        # 🔧 Periodic interruption check timer
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._check_interruption)
        self._check_timer.moveToThread(self)

        print(
            "🔧 DEBUG: BaseWorkerThread initialized with comprehensive cancellation support"
        )

    def cancel(self) -> None:
        """
        🚨 FIX: Worker megszakítása teljes interrupt mechanizmussal.

        Ez a metódus:
        1. is_cancelled flag beállítása
        2. QThread interruption request
        3. Cancellation signal emission
        4. Timer leállítása
        """
        print(
            f"🛑 DEBUG: Worker cancel requested - thread: {int(QThread.currentThreadId())}"
        )

        self.is_cancelled = True
        self.requestInterruption()  # QThread built-in interrupt
        self.cancellation_requested.emit()

        # Timer leállítása ha fut
        if self._check_timer.isActive():
            self._check_timer.stop()

        print(
            f"🛑 DEBUG: Worker cancel signals sent - thread: {int(QThread.currentThreadId())}"
        )

    def _check_interruption(self) -> None:
        """
        🔧 Periodic interruption check.

        Ez a metódus rendszeresen ellenőrzi, hogy a worker meg lett-e szakítva,
        és ha igen, graceful módon leáll.
        """
        if self.isInterruptionRequested() or self.is_cancelled:
            print("🛑 DEBUG: Interruption detected in periodic check")
            self._check_timer.stop()
            # Graceful exit a következő iteration-ben

    def emit_error(self, message: str) -> None:
        """Hibajel kibocsátása thread-safe módon."""
        self._error_message = message
        self.error_occurred.emit(message)
        print(f"❌ DEBUG: Worker error emitted: {message}")

    def emit_status(self, message: str) -> None:
        """Status update kibocsátása thread-safe módon."""
        self._status_message = message
        self.status_updated.emit(message)
        print(f"📊 DEBUG: Worker status: {message}")

    def run(self) -> None:
        """
        🚨 CRITICAL FIX: Thread run metódus teljes completion signal emission-nel.

        Ez a metódus biztosítja, hogy:
        1. Minden esetben completion_signal emission
        2. Proper exception handling
        3. Graceful cancellation support
        4. Thread cleanup
        """
        print(f"🚀 DEBUG: Worker thread started - ID: {int(QThread.currentThreadId())}")

        try:
            # Interruption check az elején
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Worker interrupted before execution")
                return

            # Periodic check timer indítása
            self._check_timer.start(1000)  # 1 másodpercenként check

            # Tényleges munka végrehajtása
            self.execute()

            # Timer leállítása
            if self._check_timer.isActive():
                self._check_timer.stop()

            if not self.is_cancelled:
                print("✅ DEBUG: Worker execution completed successfully")
                self.emit_status("✅ Befejezve")
            else:
                print("🛑 DEBUG: Worker execution cancelled")
                self.emit_status("🛑 Megszakítva")

        except Exception as e:
            # Timer leállítása error esetén
            if self._check_timer.isActive():
                self._check_timer.stop()

            if not self.is_cancelled:
                print(f"❌ DEBUG: Worker execution failed: {e}")
                self.emit_error(f"Worker hiba: {str(e)}")
                self.emit_status(f"❌ Hiba: {str(e)[:50]}...")
        finally:
            # 🚨 CRITICAL FIX: Completion signalok MINDEN esetben
            print("🔧 DEBUG: Emitting completion signals...")
            self.finished.emit()
            self.completion_signal.emit()  # ← ÚJ: Explicit completion UI-nak
            print("✅ DEBUG: Worker thread completed - all signals emitted")

    def execute(self) -> None:
        """Tényleges munkát végző metódus - override-olni kell."""
        raise NotImplementedError("A execute() metódust override-olni kell!")
