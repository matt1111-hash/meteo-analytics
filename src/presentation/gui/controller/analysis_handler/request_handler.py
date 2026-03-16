#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Analysis Handler - Request Handler

🎯 Analysis kérés kezelése

Képességek:
- Request routing
- Analysis indítás
- State kezelése

Fájl: src/presentation/gui/controller/analysis_handler/request_handler.py
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def handle_analysis_request(
    self, request_data: Dict[str, Any], provider_routing, start_analysis_callback
) -> None:
    """
    Központi elemzési kérés kezelő.

    Args:
        self: AnalysisHandler instance
        request_data: Elemzési kérés paraméterei
        provider_routing: ProviderRouting példány
        start_analysis_callback: Callback az új analysis indításához
    """
    print("=" * 80)
    print("🚨 DEBUG: AnalysisHandler.handle_analysis_request() ELEJE")
    print(f"🚨 DEBUG: analysis_type={request_data.get('analysis_type')}")
    print("=" * 80)

    from .state_management import stop_current_analysis

    logger.info(
        f"🎯 ANALYSIS REQUEST received: {request_data.get('analysis_type', 'unknown')}"
    )

    try:
        # Aktuális analysis leállítása
        if self.analysis_state["is_running"]:
            logger.info("🛑 Aktuális analysis leállítása...")
            stop_current_analysis(self)

            # Rövid várakozás a tiszta leállásra
            QTimer.singleShot(
                200,
                lambda: _start_new_analysis(
                    self, request_data, provider_routing, start_analysis_callback
                ),
            )
            return

        # Új analysis azonnali indítása
        _start_new_analysis(
            self, request_data, provider_routing, start_analysis_callback
        )

    except Exception as e:
        logger.error(f"Analysis request hiba: {e}")
        self.analysis_failed.emit(f"Elemzési kérés hiba: {e}")


def _start_new_analysis(
    self, request_data: Dict[str, Any], provider_routing, start_analysis_callback
) -> None:
    """
    ÚJ ANALYSIS INDÍTÁSA - Validálás és callback hívás.

    Args:
        self: AnalysisHandler instance
        request_data: Elemzési kérés paraméterei
        provider_routing: ProviderRouting példány
        start_analysis_callback: Callback az analysis worker elindításához
    """
    print("=" * 80)
    print("🚨 DEBUG: _start_new_analysis() ELEJE")
    print(f"🚨 DEBUG: start_analysis_callback={start_analysis_callback}")
    print("=" * 80)

    from .provider_integration import _enhance_request_with_provider_routing
    from .state_management import _cleanup_analysis_state
    from .validator import _validate_analysis_request

    try:
        # Request validálás
        from .validator import _validate_analysis_request

        if not _validate_analysis_request(self, request_data):
            return

        analysis_type = request_data.get("analysis_type", "unknown")

        # Analysis state inicializálás
        self.analysis_state = {
            "is_running": True,
            "analysis_type": analysis_type,
            "start_time": datetime.now(),
            "request_data": request_data.copy(),
        }

        # Provider routing integráció
        enhanced_request = _enhance_request_with_provider_routing(
            self, request_data, provider_routing
        )

        # Analysis worker indítása (callback)
        print("🚨 DEBUG: start_analysis_callback() HÍVÁS ELŐTT")
        success = start_analysis_callback(enhanced_request, self)
        print(f"🚨 DEBUG: start_analysis_callback() VISSZATÉRT: success={success}")

        if success:
            self.analysis_started.emit(analysis_type)
            self.status_updated.emit(
                f"🎯 {analysis_type.replace('_', ' ').title()} elemzés indítva..."
            )
            logger.info(f"✅ Analysis worker elindítva: {analysis_type}")
        else:
            logger.error("❌ Analysis worker indítás sikertelen")
            self.analysis_failed.emit("Worker indítási hiba")
            _cleanup_analysis_state(self)

    except Exception as e:
        logger.error(f"Analysis indítási hiba: {e}")
        self.analysis_failed.emit(f"Elemzés indítási hiba: {e}")
        _cleanup_analysis_state(self)
