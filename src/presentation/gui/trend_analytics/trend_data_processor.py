#!/usr/bin/env python3
"""
Trend Data Processor Module

🔥 API-alapú trend adatfeldolgozás

Képességek:
- 3178 magyar település koordináta lekérdezése
- Multi-year API hívások (5-10-55 év)
- Professional trend számítás
- Confidence interval számítás
- Statistical significance testing

Fájl: src/presentation/gui/trend_analytics/trend_data_processor.py
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from PySide6.QtCore import QObject, Signal

from ....data.city_manager import CityManager
from ....data.weather_client import WeatherClient

# Logging beállítás
logger = logging.getLogger(__name__)


class TrendDataProcessor(QObject):
    """
    🔥 TELJES ÚJRAÍRÁS: API-alapú trend adatfeldolgozás

    RÉGI: SQL lekérdezések meteo_data.db-ből
    ÚJ: Hungarian_settlements.db + Weather API + Multi-year batching

    Képességek:
    - 3178 magyar település koordináta lekérdezése
    - Multi-year API hívások (5-10-55 év)
    - Professional trend számítás
    - Confidence interval számítás
    - Statistical significance testing
    """

    # Signals for communication
    progress_updated = Signal(int)  # Progress percentage
    data_received = Signal(dict)    # Processed trend data
    error_occurred = Signal(str)    # Error message

    def __init__(self):
        super().__init__()

        # 🔥 GLOBALIZÁLT ARCHITEKTÚRA - CityManager integráció
        self.city_manager = CityManager()  # 🌍 GLOBÁLIS városkezelő (magyar + nemzetközi)
        self.weather_client = WeatherClient(preferred_provider="auto")

        # 🔥 TREND PARAMETER MAPPING (API mezők)
        self.trend_parameters = {
            "🥶 Minimum hőmérséklet": "temperature_2m_min",
            "🔥 Maximum hőmérséklet": "temperature_2m_max",
            "🌡️ Átlag hőmérséklet": "temperature_2m_mean",
            "🌧️ Csapadékmennyiség": "precipitation_sum",
            "💨 Szélsebesség": "windspeed_10m_max",
            "💨 Széllökések": "windgusts_10m_max"
        }

        # 🔥 IDŐTARTAM OPCIÓK (multi-year)
        self.time_ranges = {
            "5 év": 5,
            "10 év": 10,
            "25 év": 25,
            "55 év (teljes)": 55
        }

        logger.info("🔥 TrendDataProcessor v4.2 - GLOBALIZÁLT ARCHITEKTÚRA inicializálva")
        logger.info(f"🌍 CityManager: {self.city_manager.get_database_statistics()['total_searchable_locations']:,} kereshető helyszín")
        logger.info(f"🌍 Weather client: {self.weather_client.get_available_providers()}")

    def get_settlement_coordinates(self, settlement_name: str) -> Optional[Tuple[float, float]]:
        """
        🌍 GLOBÁLIS település koordinátáinak lekérdezése CityManager-rel

        MAGYAR PRIORITÁS: Magyar települések előnyben, majd globális városok

        Args:
            settlement_name: Település neve (pl. "Budapest", "Broxbourne", "Kiskunhalas")

        Returns:
            (latitude, longitude) tuple vagy None ha nem található
        """
        try:
            logger.info(f"🔍 GLOBÁLIS koordináta keresés: '{settlement_name}'")

            # 🌍 CityManager koordináta lekérdezés (egyesített magyar + globális)
            coordinates = self.city_manager.find_city_by_name(settlement_name)

            if coordinates:
                lat, lon = coordinates
                logger.info(f"✅ Koordináták találva: {settlement_name} -> {lat:.4f}, {lon:.4f}")
                return coordinates
            else:
                logger.warning(f"⚠️ Nem található koordináta: '{settlement_name}'")
                logger.info("💡 Próbálkozz pontosabb névvel vagy ellenőrizd a helyesírást")
                return None

        except Exception as e:
            logger.error(f"❌ Koordináta lekérdezési hiba: {e}")
            logger.exception("Koordináta keresés stacktrace:")
            return None

    def fetch_trend_data(self, settlement_name: str, parameter: str, time_range: str) -> None:
        """
        🔥 TREND ADATOK LEKÉRDEZÉSE API-VAL (háttérszálban)

        Args:
            settlement_name: Magyar település neve
            parameter: Trend paraméter (pl. "🔥 Maximum hőmérséklet")
            time_range: Időtartam (pl. "5 év")
        """
        try:
            self.progress_updated.emit(10)
            logger.info(f"🔥 TREND ANALYSIS START: {settlement_name} - {parameter} - {time_range}")

            # 1. Koordináták lekérdezése
            coordinates = self.get_settlement_coordinates(settlement_name)
            if not coordinates:
                self.error_occurred.emit(f"Nem található koordináta: {settlement_name}")
                return

            lat, lon = coordinates
            self.progress_updated.emit(20)

            # 2. Időtartam számítása
            years = self.time_ranges.get(time_range, 5)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)

            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            logger.info(f"📅 Időszak: {start_date_str} → {end_date_str} ({years} év)")
            self.progress_updated.emit(30)

            # 3. 🔥 MULTI-YEAR API HÍVÁS - BATCH FELDOLGOZÁSSAL
            logger.info(f"🌍 API hívás kezdése (batch feldolgozás): {lat:.4f}, {lon:.4f}")

            try:
                # Évenkénti batch-ek létrehozása (WeatherClient 1 éves limit miatt)
                weather_data = []
                current_start = start_date
                batch_count = 0
                total_batches = years

                while current_start < end_date:
                    # Következő év végének számítása
                    current_end = min(
                        current_start + timedelta(days=365),
                        end_date
                    )

                    current_start_str = current_start.strftime("%Y-%m-%d")
                    current_end_str = current_end.strftime("%Y-%m-%d")

                    logger.info(f"📅 Batch {batch_count + 1}/{total_batches}: {current_start_str} → {current_end_str}")

                    # 🔥 KRITIKUS JAVÍTÁS v4.2: EGYSÉGES API - weather_client hívás egyszerűsítve
                    try:
                        # ✅ EGYSZERŰSÍTETT KÓD v4.2: MINDIG List[Dict] visszatérés
                        yearly_data = self.weather_client.get_weather_data(
                            lat, lon, current_start_str, current_end_str
                        )

                        # Source kinyerése az első rekordból (data_source minden rekordba beépítve)
                        source = "unknown"
                        if yearly_data and isinstance(yearly_data, list) and len(yearly_data) > 0:
                            source = yearly_data[0].get('data_source', 'weather_api')

                        if yearly_data:
                            weather_data.extend(yearly_data)
                            logger.info(f"✅ Batch {batch_count + 1} sikeres: {len(yearly_data)} nap ({source})")
                        else:
                            logger.warning(f"⚠️ Batch {batch_count + 1} üres adattal")

                    except Exception as batch_error:
                        logger.error(f"❌ Batch {batch_count + 1} hiba: {batch_error}")
                        # Folytatjuk a következő batch-csel

                    # Következő év kezdete
                    current_start = current_end + timedelta(days=1)
                    batch_count += 1

                    # Progress frissítése
                    progress = 30 + int((batch_count / total_batches) * 30)  # 30-60%
                    self.progress_updated.emit(progress)

                logger.info(f"✅ Multi-year API hívás befejezve: {len(weather_data)} nap összesen")
                self.progress_updated.emit(60)

            except Exception as api_error:
                logger.error(f"❌ Multi-year API hiba: {api_error}")
                self.error_occurred.emit(f"API hiba: {str(api_error)}")
                return

            # 4. Adatok feldolgozása és trend számítás
            if not weather_data:
                self.error_occurred.emit("Nincs elérhető adat a kiválasztott időszakra")
                return

            # API mező mapping
            api_field = self.trend_parameters.get(parameter)
            if not api_field:
                self.error_occurred.emit(f"Ismeretlen paraméter: {parameter}")
                return

            self.progress_updated.emit(70)

            # 5. Trend számítás végrehajtása
            trend_results = self.calculate_trend_statistics(
                weather_data, api_field, settlement_name, parameter, time_range, years
            )

            self.progress_updated.emit(90)

            # 6. Eredmények visszaküldése
            if trend_results:
                self.data_received.emit(trend_results)
                logger.info(f"🎉 TREND ANALYSIS COMPLETE: {settlement_name}")
            else:
                self.error_occurred.emit("Trend számítási hiba")

            self.progress_updated.emit(100)

        except Exception as e:
            logger.error(f"❌ KRITIKUS HIBA trend lekérdezésnél: {e}")
            self.error_occurred.emit(f"Kritikus hiba: {str(e)}")

    def calculate_trend_statistics(self, weather_data: List[Dict], api_field: str,
                                 settlement_name: str, parameter: str, time_range: str, years: int) -> Optional[Dict]:
        """
        🔥 PROFESSIONAL TREND SZÁMÍTÁS API ADATOKBÓL

        Args:
            weather_data: API-ból érkező napi adatok listája
            api_field: API mező neve (pl. "temperature_2m_max")
            settlement_name, parameter, time_range, years: Metaadatok

        Returns:
            Teljes trend eredmények dictionary
        """
        try:
            logger.info(f"📊 TREND CALCULATION: {len(weather_data)} napból {api_field} feldolgozása")

            # DataFrame készítése API adatokból
            df_data = []
            for record in weather_data:
                if record.get('date') and record.get(api_field) is not None:
                    df_data.append({
                        'date': pd.to_datetime(record['date']),
                        'value': float(record[api_field])
                    })

            if len(df_data) == 0:
                logger.error(f"❌ Nincs érvényes adat a {api_field} mezőhöz")
                return None

            df = pd.DataFrame(df_data)
            df = df.sort_values('date')

            # Hiányzó adatok kezelése
            original_count = len(df)
            df = df.dropna()
            valid_count = len(df)

            if valid_count < original_count * 0.5:  # 50% alatti lefedettség
                logger.warning(f"⚠️ Alacsony adatlefedettség: {valid_count}/{original_count}")

            if valid_count < 30:  # Minimum 30 nap szükséges
                logger.error(f"❌ Túl kevés adat trend számításhoz: {valid_count}")
                return None

            logger.info(f"📈 Trend számítás: {valid_count} érvényes nap")

            # Havi aggregáció
            df['year_month'] = df['date'].dt.to_period('M')
            monthly_df = df.groupby('year_month').agg({
                'value': ['mean', 'min', 'max', 'count'],
                'date': 'first'
            }).reset_index()

            monthly_df.columns = ['year_month', 'avg_value', 'min_value', 'max_value', 'day_count', 'date']
            monthly_df = monthly_df[monthly_df['day_count'] >= 5]  # Minimum 5 nap/hónap

            if len(monthly_df) < 6:  # Minimum 6 hónap
                logger.error(f"❌ Túl kevés hónap trend számításhoz: {len(monthly_df)}")
                return None

            # 🔥 LINEÁRIS REGRESSZIÓ SZÁMÍTÁS
            X = np.arange(len(monthly_df)).reshape(-1, 1)
            y = monthly_df['avg_value'].values

            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)

            # R² és statisztikák
            r2 = r2_score(y, y_pred)

            # Trend/évtized számítás
            monthly_trend = model.coef_[0]  # havi trend
            trend_per_decade = monthly_trend * 12 * 10  # évtizedenként

            # Scipy stats további statisztikákhoz - DEFENSIVE PROGRAMMING
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
            except ValueError as ve:
                logger.error(f"❌ stats.linregress hiba: {ve}")
                # Fallback értékek
                slope = model.coef_[0]
                intercept = model.intercept_
                r_value = np.sqrt(r2)
                p_value = 0.5  # neutral érték
                std_err = 0.0

            # 🔥 CONFIDENCE INTERVAL SZÁMÍTÁS (95%) - DEFENSIVE PROGRAMMING
            try:
                n = len(y)
                t_val = stats.t.ppf(0.975, n-2)  # 95% confidence, df = n-2

                # Standard error of prediction
                y_err = np.sqrt(np.sum((y - y_pred) ** 2) / (n - 2))

                # Confidence bands
                conf_interval = t_val * y_err * np.sqrt(1 + 1/n + (X.flatten() - np.mean(X.flatten()))**2 / np.sum((X.flatten() - np.mean(X.flatten()))**2))
                ci_upper = y_pred + conf_interval
                ci_lower = y_pred - conf_interval
            except Exception as ci_error:
                logger.error(f"❌ Confidence interval számítási hiba: {ci_error}")
                # Fallback: egyszerű konfidencia sáv
                ci_upper = y_pred + np.std(y) * 0.5
                ci_lower = y_pred - np.std(y) * 0.5

            # Alapstatisztikák
            stats_dict = {
                'mean': float(np.mean(y)),
                'std': float(np.std(y)),
                'min': float(np.min(y)),
                'max': float(np.max(y)),
                'median': float(np.median(y)),
                'count': int(valid_count)
            }

            # 🔥 CHART ADATOK KÉSZÍTÉSE - DEFENSIVE PROGRAMMING
            try:
                chart_data = {
                    'dates': monthly_df['date'].tolist(),
                    'values': monthly_df['avg_value'].tolist(),
                    'trend_line': y_pred.tolist(),
                    'ci_upper': ci_upper.tolist(),
                    'ci_lower': ci_lower.tolist(),
                    'min_values': monthly_df['min_value'].tolist(),
                    'max_values': monthly_df['max_value'].tolist()
                }
            except Exception as chart_error:
                logger.error(f"❌ Chart data készítési hiba: {chart_error}")
                # Fallback: basic chart data
                chart_data = {
                    'dates': list(monthly_df['date']),
                    'values': list(monthly_df['avg_value']),
                    'trend_line': list(y_pred),
                    'ci_upper': list(ci_upper),
                    'ci_lower': list(ci_lower),
                    'min_values': list(monthly_df['min_value']),
                    'max_values': list(monthly_df['max_value'])
                }

            # 🔥 FINAL RESULTS ASSEMBLY
            results = {
                # Metaadatok
                'settlement_name': settlement_name,
                'parameter': parameter,
                'time_range': time_range,
                'api_field': api_field,
                'years': years,
                'data_source': weather_data[0].get('data_source', 'unknown') if weather_data else 'unknown',

                # Statisztikai eredmények
                'r_squared': float(r2),
                'trend_per_decade': float(trend_per_decade),
                'p_value': float(p_value),
                'slope': float(slope),
                'intercept': float(intercept),
                'std_error': float(std_err),

                # Alapstatisztikák
                'statistics': stats_dict,

                # Chart adatok
                'chart_data': chart_data,

                # Dátum információk
                'start_date': df['date'].min().strftime('%Y-%m-%d'),
                'end_date': df['date'].max().strftime('%Y-%m-%d'),
                'total_days': int(valid_count),
                'monthly_points': int(len(monthly_df))
            }

            # Trend szignifikancia értékelése
            if p_value < 0.001:
                significance = "Nagyon szignifikáns"
            elif p_value < 0.01:
                significance = "Szignifikáns"
            elif p_value < 0.05:
                significance = "Mérsékelt szignifikáns"
            else:
                significance = "Nem szignifikáns"

            results['significance'] = significance

            logger.info(f"📊 TREND RESULTS: R²={r2:.3f}, Trend={trend_per_decade:.2f}/évtized, p={p_value:.3f}")

            return results

        except Exception as e:
            logger.error(f"❌ Trend számítási hiba: {e}")
            logger.exception("Full stacktrace:")
            return None
