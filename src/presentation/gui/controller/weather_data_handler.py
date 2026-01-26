#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weather Data Handler - Időjárási adatok feldolgozása

Kezeli az időjárási adatok feldolgozását, validálását és
mentését az adatbázisba.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

from PySide6.QtCore import Slot, Signal


class WeatherDataHandler:
    """
    Időjárási adat feldolgozás kezelése.

    Felelőségek:
    - Időjárási adatok feldolgozása
    - Wind speed és wind gusts adatok kezelése
    - Napi maximum wind gusts számítás
    - Wind direction mapping (WindRose kompatibilitás)
    """

    # Signalok
    weather_data_ready = Signal(dict)
    weather_saved_to_db = Signal(bool)
    error_occurred = Signal(str)
    status_updated = Signal(str)

    def __init__(self, database_manager):
        """
        WeatherDataHandler inicializálása.

        Args:
            database_manager: DatabaseManager példány
        """
        self.database_manager = database_manager
        self._logger = logging.getLogger(__name__)
        self.current_city_data: Optional[Dict[str, Any]] = None
        self.current_weather_data: Optional[Dict[str, Any]] = None

    def set_current_city(self, city_data: Dict[str, Any]) -> None:
        """
        Jelenlegi város beállítása.

        Args:
            city_data: Város adatai
        """
        self.current_city_data = city_data

    @Slot(dict)
    def on_weather_data_completed(self, data: Dict[str, Any]) -> None:
        """
        Időjárási adatok lekérdezésének befejezése (backwards compatibility).

        Args:
            data: API válasz adatok
        """
        self._logger.info(f"🌐🌪️ on_weather_data_completed called (backwards compatibility)")

        try:
            # Provider információ kinyerése az adatokból
            used_provider = data.get('provider', 'unknown')
            self._logger.info(f"🌐 Weather data received from provider: {used_provider}")

            # Adatok feldolgozása és validálása
            processed_data = self._process_weather_data(data)

            if not processed_data:
                self.error_occurred.emit("Nincs feldolgozható időjárási adat")
                return

            # Provider információ hozzáadása a feldolgozott adatokhoz
            processed_data['provider'] = used_provider

            # Jelenlegi adatok mentése
            self.current_weather_data = processed_data

            # Adatbázisba mentés (aszinkron)
            self._save_weather_to_database(processed_data)

            # Státusz frissítése
            city_name = self.current_city_data.get('name', 'Ismeretlen') if self.current_city_data else 'Ismeretlen'
            record_count = len(processed_data.get('daily', {}).get('time', []))

            # Széllökés statisztika a státuszban
            wind_gusts_info = ""
            if 'wind_gusts_max' in processed_data.get('daily', {}):
                wind_gusts_max = processed_data['daily']['wind_gusts_max']
                if wind_gusts_max:
                    max_gust = max([g for g in wind_gusts_max if g is not None])
                    wind_gusts_info = f", max széllökés: {max_gust:.1f} km/h"

            # Provider info a státuszban
            from ..config import ProviderConfig
            provider_config = ProviderConfig()
            provider_display = provider_config.PROVIDERS.get(used_provider, {}).get('name', used_provider)

            self.status_updated.emit(
                f"🌐🌪️ Adatok sikeresen lekérdezve ({provider_display}): {city_name} ({record_count} nap{wind_gusts_info})"
            )

            # Eredmények továbbítása a GUI komponenseknek
            self._logger.info(f"📡 Emitting weather_data_ready signal...")
            self.weather_data_ready.emit(processed_data)

            self._logger.info(f"✅ Weather data befejezve: {record_count} napi rekord (backwards compatibility)")

        except Exception as e:
            self._logger.error(f"Weather data feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Adatok feldolgozási hiba: {e}")

    def _process_weather_data(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Időjárási adatok feldolgozása WIND SPEED + WIND GUSTS teljes támogatással.
        Wind direction kompatibilitási fix: winddirection_10m_dominant → wind_direction_10m_dominant

        Args:
            raw_data: Nyers API adatok

        Returns:
            Feldolgozott adatok vagy None
        """
        try:
            self._logger.info(f"🌪️🌹 Processing weather data (COMPLETE WIND DATA + WIND DIRECTION FIX)...")

            if not raw_data or 'daily' not in raw_data:
                self._logger.warning(f"⚠️ Invalid weather data structure")
                return None

            daily_data = raw_data['daily']
            hourly_data = raw_data.get('hourly', {})

            # Alapvető mezők ellenőrzése
            required_fields = ['time', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum']
            for field in required_fields:
                if field not in daily_data or not daily_data[field]:
                    self._logger.warning(f"⚠️ Hiányzó mező: {field}")
                    return None

            record_count = len(daily_data['time'])
            self._logger.info(f"🌪️🌹 Weather data valid - {record_count} records")

            # DEBUG: Eredeti adatok kulcsainak ellenőrzése
            self._logger.info(f"🌹 DEBUG: daily_data keys: {list(daily_data.keys())}")

            # Szélirány adatok ellenőrzése és debug
            if 'winddirection_10m_dominant' in daily_data:
                wind_direction_data = daily_data['winddirection_10m_dominant']
                valid_directions = [d for d in wind_direction_data if d is not None]
                self._logger.info(f"🌹 DEBUG: winddirection: {len(valid_directions)} elems")
                if valid_directions:
                    self._logger.info(f"🌹 Found wind direction data: {len(valid_directions)} valid values")
                    self._logger.info(f"🌹 Wind direction range: {min(valid_directions):.0f}° → {max(valid_directions):.0f}°")
                else:
                    self._logger.warning(f"🌹 No valid wind direction data found!")
            else:
                self._logger.warning(f"🌹 No winddirection_10m_dominant field found in daily_data!")

            # Óránkénti széllökések → napi maximum számítás
            daily_wind_gusts_max = self._calculate_daily_max_wind_gusts(
                hourly_data.get('wind_gusts_10m', []),
                hourly_data.get('time', []),
                daily_data.get('time', [])
            )

            # Feldolgozott adatok strukturált összeállítása
            processed = {
                'daily': {},  # KEZDETBEN ÜRES - Explicit feltöltés következik!
                'hourly': hourly_data,  # Óránkénti adatok megtartása
                'latitude': raw_data.get('latitude'),
                'longitude': raw_data.get('longitude'),
                'timezone': raw_data.get('timezone', 'UTC'),
                'elevation': raw_data.get('elevation'),

                # Metaadatok
                'data_source': raw_data.get('provider', 'unknown'),
                'source_type': raw_data.get('provider', 'unknown'),
                'provider': raw_data.get('provider', 'unknown'),
                'processed_at': datetime.now().isoformat(),
                'city_data': self.current_city_data.copy() if self.current_city_data else None,
                'record_count': record_count
            }

            # KRITIKUS JAVÍTÁS: Napi adatok explicit másolása, beleértve a szélsebességet is!
            required_daily_fields = [
                'time', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum',
                'windspeed_10m_max'  # EZ A HIÁNYZÓ LÁNCSZEM!
            ]

            self._logger.info(f"🌪️ Explicit copying of daily fields...")
            for field in required_daily_fields:
                if field in daily_data:
                    processed['daily'][field] = daily_data[field]
                    self._logger.debug(f"🌪️ Copied field: {field} ({len(daily_data[field])} values)")
                else:
                    self._logger.warning(f"⚠️ Missing field in daily_data: {field}")

            # További opcionális mezők másolása
            optional_daily_fields = [
                'windspeed_10m_mean', 'winddirection_10m_dominant',
                'apparent_temperature_max', 'apparent_temperature_min',
                'shortwave_radiation_sum', 'et0_fao_evapotranspiration'
            ]

            for field in optional_daily_fields:
                if field in daily_data:
                    processed['daily'][field] = daily_data[field]
                    self._logger.debug(f"🌪️ Copied optional field: {field}")

            # Napi maximum széllökések hozzáadása
            if daily_wind_gusts_max:
                processed['daily']['wind_gusts_max'] = daily_wind_gusts_max
                self._logger.info(f"🌪️ Added {len(daily_wind_gusts_max)} daily wind gusts max values")

                # Statisztika
                valid_gusts = [g for g in daily_wind_gusts_max if g is not None and g > 0]
                if valid_gusts:
                    max_gust = max(valid_gusts)
                    self._logger.info(f"🌪️ Maximum napi széllökés: {max_gust:.1f} km/h")

                    # Kritikus ellenőrzés
                    if max_gust > 100:
                        self._logger.warning(f"⚠️  KRITIKUS: Extrém széllökés detektálva: {max_gust:.1f} km/h")
                    elif max_gust > 80:
                        self._logger.warning(f"⚠️  Viharos széllökés detektálva: {max_gust:.1f} km/h")
                    elif max_gust > 60:
                        self._logger.info(f"✅ Erős széllökés detektálva: {max_gust:.1f} km/h")
                    else:
                        self._logger.info(f"✅ Mérsékelt széllökés: {max_gust:.1f} km/h")
            else:
                self._logger.warning(f"⚠️ Nincs széllökés adat az óránkénti adatokban")

            # KRITIKUS ELLENŐRZÉS: Szélsebesség adat jelenlét validálása
            if 'windspeed_10m_max' in processed['daily']:
                wind_speeds = processed['daily']['windspeed_10m_max']
                valid_speeds = [s for s in wind_speeds if s is not None and s > 0]
                if valid_speeds:
                    max_speed = max(valid_speeds)
                    avg_speed = sum(valid_speeds) / len(valid_speeds)
                    self._logger.info(f"🌪️ Szélsebesség adatok sikeresen feldolgozva:")
                    self._logger.info(f"🌪️ - Maximum szélsebesség: {max_speed:.1f} km/h")
                    self._logger.info(f"🌪️ - Átlagos szélsebesség: {avg_speed:.1f} km/h")
                    self._logger.info(f"🌪️ - Érvényes napok: {len(valid_speeds)}/{len(wind_speeds)}")
                else:
                    self._logger.warning(f"⚠️ Szélsebesség adatok üresek vagy nullák!")
            else:
                self._logger.error(f"❌ KRITIKUS: windspeed_10m_max NEM került át a feldolgozott adatokba!")
                self._logger.error(f"❌ Available daily fields: {list(processed['daily'].keys())}")
                self._logger.error(f"❌ Original daily fields: {list(daily_data.keys())}")

            self._logger.info(f"✅ Weather data processed successfully with COMPLETE WIND DATA - {record_count} records")
            self._logger.info(f"🌪️ Final processed daily fields: {list(processed['daily'].keys())}")

            # KRITIKUS SZÉLIRÁNY KOMPATIBILITÁSI FIX
            if 'winddirection_10m_dominant' in daily_data:
                processed['daily']['wind_direction_10m_dominant'] = daily_data['winddirection_10m_dominant']
                self._logger.info("✅ Wind direction data mapped for WindRoseChart compatibility.")

            return processed

        except Exception as e:
            self._logger.error(f"Weather data feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _calculate_daily_max_wind_gusts(self, hourly_gusts: List[float],
                                       hourly_times: List[str],
                                       daily_times: List[str]) -> List[float]:
        """
        Óránkénti széllökések → napi maximum konverziója.

        Args:
            hourly_gusts: Óránkénti széllökések (km/h)
            hourly_times: Óránkénti időpontok (ISO format)
            daily_times: Napi időpontok (YYYY-MM-DD format)

        Returns:
            Napi maximum széllökések listája
        """
        try:
            self._logger.info(f"🌪️ Calculating daily max wind gusts...")
            self._logger.info(f"🌪️ Hourly gusts count: {len(hourly_gusts)}")
            self._logger.info(f"🌪️ Hourly times count: {len(hourly_times)}")
            self._logger.info(f"🌪️ Daily times count: {len(daily_times)}")

            if not hourly_gusts or not hourly_times or not daily_times:
                self._logger.warning(f"⚠️ Missing data for wind gusts calculation")
                return []

            # Óránkénti adatok DataFrame-be konvertálása
            hourly_df = pd.DataFrame({
                'time': pd.to_datetime(hourly_times),
                'wind_gusts': hourly_gusts
            })

            # Datum oszlop hozzáadása (óránkénti időpontokból)
            hourly_df['date'] = hourly_df['time'].dt.date

            # Napi maximumok számítása
            daily_max_gusts = []

            for daily_time in daily_times:
                try:
                    # Napi dátum konvertálása
                    daily_date = pd.to_datetime(daily_time).date()

                    # Adott nap óránkénti széllökései
                    day_gusts = hourly_df[hourly_df['date'] == daily_date]['wind_gusts']

                    if not day_gusts.empty:
                        # Csak érvényes értékek (nem None, nem NaN)
                        valid_gusts = day_gusts.dropna()

                        if not valid_gusts.empty:
                            daily_max = valid_gusts.max()
                            daily_max_gusts.append(daily_max)

                            # Debug logolás minden 10. naphoz
                            if len(daily_max_gusts) % 10 == 0:
                                self._logger.debug(f"🌪️ Day {daily_time}: max gust {daily_max:.1f} km/h")
                        else:
                            # Nincs érvényes széllökés adat erre a napra
                            daily_max_gusts.append(None)
                    else:
                        # Nincs óránkénti adat erre a napra
                        daily_max_gusts.append(None)

                except Exception as e:
                    self._logger.warning(f"⚠️ Error processing day {daily_time}: {e}")
                    daily_max_gusts.append(None)

            # Eredmény validálás
            valid_gusts = [g for g in daily_max_gusts if g is not None and g > 0]

            if valid_gusts:
                max_overall = max(valid_gusts)
                avg_gusts = sum(valid_gusts) / len(valid_gusts)

                self._logger.info(f"🌪️ Daily wind gusts calculation complete:")
                self._logger.info(f"🌪️ - Valid days: {len(valid_gusts)}/{len(daily_max_gusts)}")
                self._logger.info(f"🌪️ - Maximum overall: {max_overall:.1f} km/h")
                self._logger.info(f"🌪️ - Average gusts: {avg_gusts:.1f} km/h")

                # Kritikus ellenőrzés
                if max_overall > 120:
                    self._logger.critical(f"🚨 KRITIKUS: Hurrikán erősségű széllökés: {max_overall:.1f} km/h")
                elif max_overall > 100:
                    self._logger.warning(f"⚠️  KRITIKUS: Extrém széllökés: {max_overall:.1f} km/h")
                elif max_overall > 80:
                    self._logger.warning(f"⚠️  Viharos széllökés: {max_overall:.1f} km/h")
                else:
                    self._logger.info(f"✅ Mérsékelt széllökés: {max_overall:.1f} km/h")

            else:
                self._logger.warning(f"⚠️ Nincs érvényes széllökés adat")

            return daily_max_gusts

        except Exception as e:
            self._logger.error(f"Daily wind gusts calculation error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _save_weather_to_database(self, weather_data: Dict[str, Any]) -> None:
        """
        Időjárási adatok mentése adatbázisba.

        Args:
            weather_data: Feldolgozott időjárási adatok
        """
        try:
            success = self.database_manager.save_weather_to_database(
                weather_data, self.current_city_data
            )
            self.weather_saved_to_db.emit(success)
        except Exception as e:
            self._logger.error(f"Adatbázis mentési hiba: {e}")
            self.weather_saved_to_db.emit(False)

    def get_current_weather_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi időjárási adatok lekérdezése."""
        return self.current_weather_data.copy() if self.current_weather_data else None

    def get_current_city_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi város adatainak lekérdezése."""
        return self.current_city_data.copy() if self.current_city_data else None
