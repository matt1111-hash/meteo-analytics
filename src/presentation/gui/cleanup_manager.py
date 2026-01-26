#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup Manager Module
Felelős az alkalmazás worker thread-jeinek és erőforrásainak biztonságos leállításáért.
A MainWindowból kiszervezve a jobb szervezettség és karbantarthatóság érdekében.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .windows.main_window import MainWindow


class CleanupManager:
    """
    Kezeli az alkalmazás összes worker thread-je és erőforrásának leállítását.
    
    Ez az osztály biztosítja, hogy az alkalmazás bezárásakor minden háttérfolyamat,
    worker és erőforrás (pl. QWebEngineView) megfelelően leálljon, elkerülve a
    memóriaszivárgást és a fennakadásokat.
    """

    def __init__(self, main_window: 'MainWindow'):
        """
        CleanupManager inicializálása.
        
        Args:
            main_window: A MainWindow példány, amelynek a komponenseit kezeli.
        """
        self.mw = main_window

    def cleanup_all(self) -> None:
        """
        Összes worker és erőforrás leállítása a megfelelő sorrendben.
        """
        print("🧹 CleanupManager: Starting comprehensive cleanup sequence...")

        # 1. WebEngine views cleanup (első helyen - JavaScript bridge problémák elkerülése)
        self._cleanup_all_web_engines()

        # 2. Workers cleanup (második helyen - aktív műveletek leállítása)
        self._cleanup_all_workers()

        # 3. Threads cleanup (harmadik helyen - thread resources felszabadítása)
        self._cleanup_all_threads()

        # 4. Timers cleanup (negyedik helyen - timer resources felszabadítása)
        self._cleanup_all_timers()

        # 5. Clear all references
        if hasattr(self.mw, 'active_threads'):
            self.mw.active_threads.clear()
        if hasattr(self.mw, 'active_workers'):
            self.mw.active_workers.clear()
        if hasattr(self.mw, 'web_engine_views'):
            self.mw.web_engine_views.clear()
        if hasattr(self.mw, 'cleanup_timers'):
            self.mw.cleanup_timers.clear()

        print("✅ CleanupManager: Cleanup sequence completed.")

    def _cleanup_all_threads(self) -> None:
        """🧹 KRITIKUS: Összes aktív thread graceful cleanup-ja."""
        if not hasattr(self.mw, 'active_threads'):
            return

        print(f"🧹 CleanupManager: Starting thread cleanup - {len(self.mw.active_threads)} threads")

        for thread in self.mw.active_threads[:]:  # Copy to avoid modification during iteration
            try:
                if thread.isRunning():
                    print(f"🧹 CleanupManager: Stopping thread: {thread}")

                    # Graceful shutdown request
                    thread.quit()

                    # Wait for thread to finish (max 5 seconds)
                    if not thread.wait(5000):
                        print(f"⚠️ CleanupManager: Thread did not finish gracefully, terminating: {thread}")
                        thread.terminate()
                        thread.wait(2000)  # Wait for termination

                    # Clean up
                    thread.deleteLater()
                    print(f"✅ CleanupManager: Thread cleaned up: {thread}")

                self.mw.active_threads.remove(thread)

            except Exception as e:
                print(f"⚠️ CleanupManager: Thread cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if thread in self.mw.active_threads:
                    self.mw.active_threads.remove(thread)

        print("✅ CleanupManager: All threads cleaned up")

    def _cleanup_all_workers(self) -> None:
        """🧹 KRITIKUS: Összes aktív worker graceful cleanup-ja."""
        if not hasattr(self.mw, 'active_workers'):
            return

        print(f"🧹 CleanupManager: Starting worker cleanup - {len(self.mw.active_workers)} workers")

        for worker in self.mw.active_workers[:]:  # Copy to avoid modification during iteration
            try:
                print(f"🧹 CleanupManager: Stopping worker: {worker}")

                # Stop worker if it has a stop method
                if hasattr(worker, 'stop'):
                    worker.stop()
                elif hasattr(worker, 'cancel'):
                    worker.cancel()
                elif hasattr(worker, 'quit'):
                    worker.quit()

                # If worker has a thread, clean it up
                if hasattr(worker, 'thread'):
                    thread = worker.thread()
                    if thread and thread.isRunning():
                        thread.quit()
                        thread.wait(3000)

                # Clean up worker
                worker.deleteLater()
                print(f"✅ CleanupManager: Worker cleaned up: {worker}")

                self.mw.active_workers.remove(worker)

            except Exception as e:
                print(f"⚠️ CleanupManager: Worker cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if worker in self.mw.active_workers:
                    self.mw.active_workers.remove(worker)

        print("✅ CleanupManager: All workers cleaned up")

    def _cleanup_all_web_engines(self) -> None:
        """🧹 KRITIKUS: Összes WebEngine view graceful cleanup-ja."""
        if not hasattr(self.mw, 'web_engine_views'):
            return

        print(f"🧹 CleanupManager: Starting WebEngine cleanup - {len(self.mw.web_engine_views)} views")

        for web_view in self.mw.web_engine_views[:]:  # Copy to avoid modification during iteration
            try:
                print(f"🧹 CleanupManager: Stopping WebEngine view: {web_view}")

                # Stop loading and clear content
                web_view.stop()
                web_view.setUrl("")

                # Clean up
                web_view.deleteLater()
                print(f"✅ CleanupManager: WebEngine view cleaned up: {web_view}")

                self.mw.web_engine_views.remove(web_view)

            except Exception as e:
                print(f"⚠️ CleanupManager: WebEngine cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if web_view in self.mw.web_engine_views:
                    self.mw.web_engine_views.remove(web_view)

        print("✅ CleanupManager: All WebEngine views cleaned up")

    def _cleanup_all_timers(self) -> None:
        """🧹 KRITIKUS: Összes QTimer graceful cleanup-ja."""
        if not hasattr(self.mw, 'cleanup_timers'):
            return

        print(f"🧹 CleanupManager: Starting timer cleanup - {len(self.mw.cleanup_timers)} timers")

        for timer in self.mw.cleanup_timers[:]:  # Copy to avoid modification during iteration
            try:
                print(f"🧹 CleanupManager: Stopping timer: {timer}")

                # Stop timer
                if timer.isActive():
                    timer.stop()

                # Clean up
                timer.deleteLater()
                print(f"✅ CleanupManager: Timer cleaned up: {timer}")

                self.mw.cleanup_timers.remove(timer)

            except Exception as e:
                print(f"⚠️ CleanupManager: Timer cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if timer in self.mw.cleanup_timers:
                    self.mw.cleanup_timers.remove(timer)

        print("✅ CleanupManager: All timers cleaned up")


# Export
__all__ = ['CleanupManager']
