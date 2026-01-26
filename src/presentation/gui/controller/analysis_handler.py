#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysis Handler - Analysis request kezelése

Kezeli az elemzési kéréseket, worker lifecycle-t,
és a provider routing integrációt.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Slot, Signal, QTimer


class AnalysisHandler(QObject):
    """
    Analysis request kezelése.

    Felelőségek:
    - Analysis request routing (single/multi-city/county)
    - Worker lifecycle management
    - Request validálás
    - Analysis state kezelés
    """

    # Signalok
    analysis_started = Signal(str)              # analysis_type
    analysis_progress = Signal(str, int)        # message, percentage
    analysis_completed = Signal(dict)           # result_data
    analysis_failed = Signal(str)               # error_message
    analysis_cancelled = Signal()               # megszakítás megerősítése
    status_updated = Signal(str)                # str - státusz üzenet

    def __init__(self, parent=None):
        """
        AnalysisHandler inicializálása.

        Args:
            parent: Szülő QObject (általában AppController)
        """
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)

        # Analysis state
        self.active_analysis_worker = None
        self.analysis_state = {
            'is_running': False,
            'analysis_type': None,
            'start_time': None,
            'request_data': None
        }

    @Slot(dict)
    def handle_analysis_request(self, request_data: Dict[str, Any],
                                provider_routing, start_analysis_callback) -> None:
        """
        Központi elemzési kérés kezelő.

        Args:
            request_data: Elemzési kérés paraméterei
            provider_routing: ProviderRouting példány
            start_analysis_callback: Callback az új analysis indításához
        """
        self._logger.info(f"🎯 ANALYSIS REQUEST received: {request_data.get('analysis_type', 'unknown')}")

        try:
            # Aktuális analysis leállítása
            if self.analysis_state['is_running']:
                self._logger.info("🛑 Aktuális analysis leállítása...")
                self.stop_current_analysis()

                # Rövid várakozás a tiszta leállásra
                QTimer.singleShot(200, lambda: self._start_new_analysis(
                    request_data, provider_routing, start_analysis_callback
                ))
                return

            # Új analysis azonnali indítása
            self._start_new_analysis(request_data, provider_routing, start_analysis_callback)

        except Exception as e:
            self._logger.error(f"Analysis request hiba: {e}")
            self.analysis_failed.emit(f"Elemzési kérés hiba: {e}")

    def _start_new_analysis(self, request_data: Dict[str, Any],
                            provider_routing, start_analysis_callback) -> None:
        """
        ÚJ ANALYSIS INDÍTÁSA - Validálás és callback hívás.

        Args:
            request_data: Elemzési kérés paraméterei
            provider_routing: ProviderRouting példány
            start_analysis_callback: Callback az analysis worker elindításához
        """
        try:
            # Request validálás
            if not self._validate_analysis_request(request_data):
                return

            analysis_type = request_data.get('analysis_type', 'unknown')

            # Analysis state inicializálás
            self.analysis_state = {
                'is_running': True,
                'analysis_type': analysis_type,
                'start_time': datetime.now(),
                'request_data': request_data.copy()
            }

            # Provider routing integráció
            enhanced_request = self._enhance_request_with_provider_routing(
                request_data, provider_routing
            )

            # Analysis worker indítása (callback)
            success = start_analysis_callback(enhanced_request, self)

            if success:
                self.analysis_started.emit(analysis_type)
                self.status_updated.emit(f"🎯 {analysis_type.replace('_', ' ').title()} elemzés indítva...")
                self._logger.info(f"✅ Analysis worker elindítva: {analysis_type}")
            else:
                self._logger.error("❌ Analysis worker indítás sikertelen")
                self.analysis_failed.emit("Worker indítási hiba")
                self._cleanup_analysis_state()

        except Exception as e:
            self._logger.error(f"Analysis indítási hiba: {e}")
            self.analysis_failed.emit(f"Elemzés indítási hiba: {e}")
            self._cleanup_analysis_state()

    def _validate_analysis_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Analysis request validálás - koordináta kulcsok kompatibilitással.

        Args:
            request_data: Kérés adatok

        Returns:
            bool: Valid-e a kérés
        """
        try:
            # Kötelező mezők ellenőrzése
            required_fields = ['analysis_type', 'date_range']
            for field in required_fields:
                if field not in request_data:
                    self.analysis_failed.emit(f"Hiányzó kötelező mező: {field}")
                    return False

            analysis_type = request_data.get('analysis_type')
            valid_types = ['single_location', 'multi_city', 'county_analysis']

            if analysis_type not in valid_types:
                self.analysis_failed.emit(f"Érvénytelen elemzés típus: {analysis_type}")
                return False

            # Dátum range validálás
            date_range = request_data.get('date_range', {})
            if not date_range.get('start_date') or not date_range.get('end_date'):
                self.analysis_failed.emit("Hiányzó dátum tartomány")
                return False

            try:
                start_date_value = datetime.strptime(date_range.get('start_date', ''), "%Y-%m-%d")
                end_date_value = datetime.strptime(date_range.get('end_date', ''), "%Y-%m-%d")
            except ValueError as exc:
                self.analysis_failed.emit(f"Érvénytelen dátum formátum: {exc}")
                return False

            if (end_date_value - start_date_value).days > 60 * 365:
                error_message = "Maximum 60 éves időszak kérdezhető le"
                self.status_updated.emit(error_message)
                self.analysis_failed.emit(error_message)
                return False

            # Lokáció validálás koordináta kulcsok kompatibilitással
            if analysis_type == 'single_location':
                if not self._validate_single_location_coords(request_data):
                    return False

            elif analysis_type in ['multi_city', 'county_analysis']:
                if not request_data.get('region_name') and not request_data.get('county_name'):
                    self.analysis_failed.emit("Hiányzó régió vagy megye név")
                    return False

            self._logger.info(f"✅ Analysis request validation OK: {analysis_type}")
            return True

        except Exception as e:
            self._logger.error(f"Request validation hiba: {e}")
            self.analysis_failed.emit(f"Kérés validálási hiba: {e}")
            return False

    def _validate_single_location_coords(self, request_data: Dict[str, Any]) -> bool:
        """
        Single location koordináták validálása (koordináta kulcsok kompatibilitással).

        Args:
            request_data: Kérés adatok

        Returns:
            bool: Validak-e a koordináták
        """
        has_direct_coords = False
        has_location_data_coords = False

        # 1. Direkt koordináták ellenőrzése
        if 'latitude' in request_data and 'longitude' in request_data:
            has_direct_coords = True
            self._logger.info("🔧 Found direct coordinates: latitude/longitude")
        elif 'lat' in request_data and 'lon' in request_data:
            has_direct_coords = True
            self._logger.info("🔧 Found direct coordinates: lat/lon")

        # 2. location_data objektum ellenőrzése
        location_data = request_data.get('location_data', {})
        if location_data:
            lat_keys = ['lat', 'latitude']
            lon_keys = ['lon', 'longitude']

            has_lat = any(key in location_data for key in lat_keys)
            has_lon = any(key in location_data for key in lon_keys)

            if has_lat and has_lon:
                has_location_data_coords = True
                self._logger.info("🔧 Found location_data coordinates")

        # Koordináták validálása
        if not (has_direct_coords or has_location_data_coords):
            error_msg = "Hiányzó lokáció koordináták"
            self._logger.error(f"🔧 COORDINATE VALIDATION FAILED: {error_msg}")
            self._logger.error(f"🔧 Request keys: {list(request_data.keys())}")
            if location_data:
                self._logger.error(f"🔧 location_data keys: {list(location_data.keys())}")

            self.analysis_failed.emit(error_msg)
            return False

        self._logger.info("✅ Single location coordinates validation passed")
        return True

    def _enhance_request_with_provider_routing(self, request_data: Dict[str, Any],
                                              provider_routing) -> Dict[str, Any]:
        """
        Provider routing integráció - Kérés gazdagítása provider információkkal.

        Args:
            request_data: Eredeti kérés
            provider_routing: ProviderRouting példány

        Returns:
            Gazdagított kérés provider routing információkkal
        """
        try:
            enhanced_request = request_data.copy()

            # Koordináták kinyerése
            latitude, longitude = self._extract_coordinates_from_request(request_data)

            if latitude is not None and longitude is not None:
                # Smart provider selection
                date_range = request_data.get('date_range', {})
                selected_provider = provider_routing.select_provider_for_request(
                    latitude, longitude,
                    date_range.get('start_date', ''),
                    date_range.get('end_date', '')
                )

                # Provider információk hozzáadása
                enhanced_request['selected_provider'] = selected_provider
                enhanced_request['provider_config'] = provider_routing.provider_config.PROVIDERS.get(selected_provider, {})

                # Usage tracking
                provider_routing.track_provider_usage(selected_provider)

                self._logger.info(f"🌐 Provider routing: {selected_provider} selected")
            else:
                # Fallback provider
                enhanced_request['selected_provider'] = 'open-meteo'
                self._logger.warning("🌐 No coordinates found, using fallback provider")

            return enhanced_request

        except Exception as e:
            self._logger.error(f"Provider routing enhancement hiba: {e}")
            return request_data

    def _extract_coordinates_from_request(self, request_data: Dict[str, Any]) -> tuple:
        """
        Koordináták kinyerése a kérésből az elemzés típusa alapján.

        Args:
            request_data: Kérés adatok

        Returns:
            (latitude, longitude) tuple vagy (None, None)
        """
        analysis_type = request_data.get('analysis_type')

        if analysis_type == 'single_location':
            # 1. Direkt koordináták keresése
            if 'latitude' in request_data and 'longitude' in request_data:
                return request_data.get('latitude'), request_data.get('longitude')
            elif 'lat' in request_data and 'lon' in request_data:
                return request_data.get('lat'), request_data.get('lon')

            # 2. location_data objektum ellenőrzése
            location_data = request_data.get('location_data', {})
            if location_data:
                lat = location_data.get('latitude') or location_data.get('lat')
                lon = location_data.get('longitude') or location_data.get('lon')

                if lat is not None and lon is not None:
                    return lat, lon

        elif analysis_type in ['multi_city', 'county_analysis']:
            # Multi-city esetén használjuk a jelenlegi város koordinátáit (ha van)
            # Ez a kontexterületből kellene jöjjön
            return 47.4979, 19.0402  # Budapest default

        return None, None

    @Slot(str, int)
    def on_analysis_progress(self, message: str, percentage: int) -> None:
        """Analysis progress frissítése"""
        self.analysis_progress.emit(message, percentage)
        self.status_updated.emit(f"📊 {message} ({percentage}%)")
        self._logger.debug(f"📊 Analysis progress: {message} - {percentage}%")

    @Slot(dict)
    def on_analysis_completed(self, result_data: dict) -> None:
        """Analysis befejezése sikeresen"""
        try:
            self._logger.info("✅ Analysis completed successfully")

            # Eredmény feldolgozása típus alapján
            processed_result = self._process_analysis_result(result_data)

            # State cleanup
            analysis_type = self.analysis_state.get('analysis_type', 'unknown')
            duration = self._calculate_analysis_duration()

            # Success signalok
            self.analysis_completed.emit(processed_result)
            self.status_updated.emit(f"✅ {analysis_type.replace('_', ' ').title()} elemzés befejezve ({duration:.1f}s)")

            # Cleanup
            self._cleanup_analysis_state()

        except Exception as e:
            self._logger.error(f"Analysis result processing hiba: {e}")
            self.analysis_failed.emit(f"Eredmény feldolgozási hiba: {e}")

    @Slot(str)
    def on_analysis_failed(self, error_message: str) -> None:
        """Analysis hiba kezelése"""
        self._logger.error(f"❌ Analysis failed: {error_message}")
        self.analysis_failed.emit(error_message)
        self.status_updated.emit(f"❌ Elemzési hiba: {error_message}")
        self._cleanup_analysis_state()

    @Slot()
    def on_analysis_cancelled(self) -> None:
        """Analysis megszakítás kezelése"""
        self._logger.info("ℹ️ Analysis cancelled")
        self.analysis_cancelled.emit()
        self.status_updated.emit("ℹ️ Elemzés megszakítva")
        self._cleanup_analysis_state()

    def _process_analysis_result(self, result_data: dict) -> dict:
        """
        Analysis eredmény feldolgozása és strukturálása.

        Args:
            result_data: Nyers worker eredmény

        Returns:
            Feldolgozott és strukturált eredmény
        """
        try:
            analysis_type = self.analysis_state.get('analysis_type', 'unknown')

            processed_result = {
                'analysis_type': analysis_type,
                'request_data': self.analysis_state.get('request_data', {}),
                'result_data': result_data.get('result_data', {}),
                'metadata': {
                    'provider': result_data.get('provider', 'unknown'),
                    'timestamp': result_data.get('timestamp'),
                    'duration': self._calculate_analysis_duration(),
                    'success': result_data.get('success', True)
                }
            }

            # Típus-specifikus feldolgozás
            if analysis_type == 'single_location':
                pass  # Single location eredmény további feldolgozása (ha szükséges)
            elif analysis_type in ['multi_city', 'county_analysis']:
                processed_result['city_count'] = len(result_data.get('result_data', {}).get('cities', []))

            return processed_result

        except Exception as e:
            self._logger.error(f"Result processing hiba: {e}")
            return result_data

    def _calculate_analysis_duration(self) -> float:
        """Analysis időtartam számítása másodpercben"""
        start_time = self.analysis_state.get('start_time')
        if start_time:
            return (datetime.now() - start_time).total_seconds()
        return 0.0

    def _cleanup_analysis_state(self) -> None:
        """Analysis state és worker cleanup"""
        try:
            # Worker cleanup
            if self.active_analysis_worker:
                if self.active_analysis_worker.isRunning():
                    self.active_analysis_worker.stop_analysis()

                # Disconnect signalok
                try:
                    self.active_analysis_worker.progress_updated.disconnect()
                    self.active_analysis_worker.analysis_completed.disconnect()
                    self.active_analysis_worker.analysis_failed.disconnect()
                    self.active_analysis_worker.analysis_cancelled.disconnect()
                except Exception:
                    pass

                # Worker törlése
                self.active_analysis_worker.deleteLater()
                self.active_analysis_worker = None

            # State reset
            self.analysis_state = {
                'is_running': False,
                'analysis_type': None,
                'start_time': None,
                'request_data': None
            }

            self._logger.info("🧹 Analysis state cleaned up")

        except Exception as e:
            self._logger.error(f"Cleanup hiba: {e}")

    def stop_current_analysis(self) -> None:
        """
        AKTUÁLIS ANALYSIS LEÁLLÍTÁSA
        Graceful shutdown - nem brutális terminálás
        """
        try:
            if not self.analysis_state['is_running']:
                self._logger.info("🛑 Nincs futó analysis amit meg lehetne szakítani")
                return

            analysis_type = self.analysis_state.get('analysis_type', 'unknown')
            self._logger.info(f"🛑 Analysis megszakítása: {analysis_type}")

            if self.active_analysis_worker:
                self.active_analysis_worker.stop_analysis()

            # State update
            self.status_updated.emit("🛑 Elemzés megszakítása...")

        except Exception as e:
            self._logger.error(f"Analysis stop hiba: {e}")

    def is_analysis_running(self) -> bool:
        """Analysis futási állapot lekérdezése"""
        return self.analysis_state.get('is_running', False)

    def get_current_analysis_info(self) -> Dict[str, Any]:
        """Jelenlegi analysis információk lekérdezése"""
        return self.analysis_state.copy()

    def set_active_worker(self, worker) -> None:
        """
        Aktív analysis worker beállítása.

        Args:
            worker: AnalysisWorker példány
        """
        self.active_analysis_worker = worker
