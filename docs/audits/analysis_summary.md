# Projekt Analízis Riport: global_weather_analyzer

**Generálva:** 2025-11-25T16:45:00.664104

---

## 1. 📊 Gyors Összegzés

- **Modulok:** 111
- **LOC (összesen):** 33,998
- **Osztályok:** 191
- **Függvények:** 342
- **Ciklusok:** 2
- **External deps:** 51
- **Layer violations:** 0

## 2. 🔥 Refaktorációs Prioritások (Hotspotok)

### God Classes (LOC > 300)
- **ultimate_project_analyzer.ReportGenerator**: 599 LOC
- **src.data.anomaly_profile_manager.AnomalyProfileManager**: 351 LOC
- **src.gui.map_visualizer.FoliumMapGenerator**: 628 LOC
- **src.gui.map_visualizer.HungarianMapVisualizer**: 705 LOC
- **src.gui.universal_location_selector.UniversalLocationSelector**: 379 LOC
- **src.gui.hungarian_location_selector.HungarianLocationSelector**: 675 LOC
- **src.gui.hungarian_map_tab.HungarianMapTab**: 1312 LOC
- **src.gui.color_palette.ColorPalette**: 447 LOC
- **src.gui.analytics_view.AnalyticsView**: 828 LOC
- **src.gui.control_panel.ControlPanel**: 609 LOC
- **src.gui.theme_manager.ProfessionalThemeManager**: 448 LOC

### Complex Functions/Methods (Top 10)
- **src.gui.hungarian_map_tab.HungarianMapTab**: LOC=1312, CC=1
- **src.gui.main_window.MainWindow**: LOC=1170, CC=1
- **src.gui.app_controller.AppController**: LOC=1107, CC=1
- **src.gui.analytics_view.AnalyticsView**: LOC=828, CC=1
- **src.gui.results_panel.results_panel.ResultsPanel**: LOC=738, CC=1
- **src.gui.panel_widgets.query_control_widget.QueryControlWidget**: LOC=717, CC=1
- **src.gui.map_visualizer.HungarianMapVisualizer**: LOC=705, CC=1
- **src.gui.hungarian_location_selector.HungarianLocationSelector**: LOC=675, CC=1
- **src.gui.map_visualizer.FoliumMapGenerator**: LOC=628, CC=1
- **src.gui.control_panel.ControlPanel**: LOC=609, CC=1

### Mixed Layers (UI + ML)
✅ Nem találtunk réteg keveredést.

## 3. 🕸️  Import Gráf Áttekintés

### Top 10 Fan-In (Legtöbb bejövő függőség)
- **src.gui.theme_manager**: 33 bejövő
- **src.data.enums**: 13 bejövő
- **src.data.models**: 11 bejövő
- **src.analytics.multi_city_engine**: 10 bejövő
- **src.domain.analytics.models**: 9 bejövő
- **src.gui.utils**: 9 bejövő
- **src.gui.charts.base_chart**: 7 bejövő
- **src.infrastructure.repositories.city_repository**: 6 bejövő
- **src.domain.analytics.services**: 6 bejövő
- **src.gui.color_palette**: 6 bejövő

### Top 10 Fan-Out (Legtöbb kimenő függőség)
- **src.gui.main_window**: 12 kimenő
- **src.analytics.multi_city_engine**: 9 kimenő
- **src.gui.control_panel**: 9 kimenő
- **src.gui.hungarian_map_tab**: 7 kimenő
- **src.gui.analytics_view**: 7 kimenő
- **src.gui.results_panel.results_panel**: 7 kimenő
- **src.gui.results_panel.extreme_events_tab**: 7 kimenő
- **tests.application.use_cases.test_analyze_multi_city**: 6 kimenő
- **src.api.routes.detailed_city**: 6 kimenő
- **src.api.routes.single_city**: 6 kimenő

### Circular Dependencies
⚠️ **2 ciklus találva:**

- src.gui.utils → src.gui.theme_manager → src.gui.color_palette → src.gui.utils
- src.gui.results_panel → src.gui.results_panel

## 4. 📦 Részletes Modul Breakdown (Top 50)

### src.gui.map_visualizer
- **LOC:** 1708
- **Classes:** 6
- **Functions:** 17
- **Fan-In:** 1
- **Fan-Out:** 2
- **Classes:**
  - `FoliumMapConfig`: 27 LOC, 1 CC
  - `LocalHttpServerThread`: 44 LOC, 1 CC
  - `QuietHTTPRequestHandler`: 3 LOC, 1 CC
  - `JavaScriptBridge`: 34 LOC, 1 CC
  - `FoliumMapGenerator`: 628 LOC, 1 CC
- **Functions:**
  - `stop`: 8 LOC, 2 CC
  - `demo_http_server_folium_map_visualizer`: 218 LOC, 9 CC
  - `on_map_ready`: 14 LOC, 4 CC
  - `on_county_clicked`: 2 LOC, 1 CC
  - `on_coordinates_clicked`: 2 LOC, 1 CC

### src.gui.hungarian_map_tab
- **LOC:** 1581
- **Classes:** 1
- **Functions:** 22
- **Fan-In:** 1
- **Fan-Out:** 7
- **Classes:**
  - `HungarianMapTab`: 1312 LOC, 1 CC
- **Functions:**
  - `demo_hungarian_map_tab_analytics_sync_parameter_memory`: 222 LOC, 3 CC
  - `on_location_selected`: 2 LOC, 1 CC
  - `on_county_clicked_on_map`: 2 LOC, 1 CC
  - `on_map_interaction`: 2 LOC, 1 CC
  - `on_export_completed`: 2 LOC, 1 CC

### src.gui.utils
- **LOC:** 1352
- **Classes:** 7
- **Functions:** 42
- **Fan-In:** 9
- **Fan-Out:** 1
- **Classes:**
  - `APIConstants`: 21 LOC, 1 CC
  - `GUIConstants`: 35 LOC, 1 CC
  - `ThemeType`: 6 LOC, 1 CC
  - `ColorVariant`: 8 LOC, 1 CC
  - `StyleSheets`: 189 LOC, 1 CC
- **Functions:**
  - `get_optimal_data_source`: 16 LOC, 5 CC
  - `get_source_display_name`: 9 LOC, 1 CC
  - `validate_api_source_available`: 15 LOC, 4 CC
  - `get_fallback_source_chain`: 16 LOC, 2 CC
  - `log_api_source_selection`: 10 LOC, 1 CC

### src.gui.analytics_view
- **LOC:** 1314
- **Classes:** 9
- **Functions:** 5
- **Fan-In:** 1
- **Fan-Out:** 7
- **Classes:**
  - `MeteorologicalColorMaps`: 70 LOC, 1 CC
  - `RecordCard`: 43 LOC, 1 CC
  - `RecordSummaryCard`: 55 LOC, 1 CC
  - `TemperatureTabWidget`: 22 LOC, 1 CC
  - `PrecipitationTabWidget`: 26 LOC, 1 CC
- **Functions:**
  - `safe_max`: 6 LOC, 2 CC
  - `safe_min`: 6 LOC, 2 CC
  - `safe_avg`: 6 LOC, 2 CC
  - `safe_sum`: 6 LOC, 2 CC
  - `safe_count`: 6 LOC, 2 CC

### ultimate_project_analyzer
- **LOC:** 1221
- **Classes:** 9
- **Functions:** 1
- **Fan-In:** 0
- **Fan-Out:** 0
- **Classes:**
  - `FunctionInfo`: 10 LOC, 1 CC
  - `ClassInfo`: 11 LOC, 1 CC
  - `ModuleInfo`: 14 LOC, 1 CC
  - `CouplingMetrics`: 13 LOC, 1 CC
  - `AnalysisResult`: 16 LOC, 1 CC
- **Functions:**
  - `main`: 58 LOC, 1 CC

### src.gui.main_window
- **LOC:** 1213
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 3
- **Fan-Out:** 12
- **Classes:**
  - `MainWindow`: 1170 LOC, 1 CC

### src.data.models
- **LOC:** 1205
- **Classes:** 13
- **Functions:** 7
- **Fan-In:** 11
- **Fan-Out:** 1
- **Classes:**
  - `LocationType`: 9 LOC, 1 CC
  - `TimeGranularity`: 9 LOC, 1 CC
  - `AnalysisType`: 10 LOC, 1 CC
  - `Location`: 165 LOC, 1 CC
  - `UniversalLocation`: 99 LOC, 1 CC
- **Functions:**
  - `create_universal_location`: 38 LOC, 2 CC
  - `create_universal_time_range`: 38 LOC, 4 CC
  - `create_universal_query`: 37 LOC, 2 CC
  - `create_analytics_question`: 25 LOC, 1 CC
  - `create_city_weather_result`: 37 LOC, 1 CC

### src.gui.app_controller
- **LOC:** 1131
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `AppController`: 1107 LOC, 1 CC

### src.gui.results_panel.results_panel
- **LOC:** 1067
- **Classes:** 8
- **Functions:** 1
- **Fan-In:** 0
- **Fan-Out:** 7
- **Classes:**
  - `_DummyPandas`: 7 LOC, 1 CC
  - `QuickOverviewTab`: 8 LOC, 1 CC
  - `DetailedChartsTab`: 8 LOC, 1 CC
  - `DataTableTab`: 8 LOC, 1 CC
  - `ExtremeEventsTab`: 8 LOC, 1 CC
- **Functions:**
  - `create_results_panel`: 9 LOC, 1 CC

### src.gui.workers.data_fetch_worker
- **LOC:** 946
- **Classes:** 6
- **Functions:** 12
- **Fan-In:** 2
- **Fan-Out:** 0
- **Classes:**
  - `APIConstants`: 4 LOC, 1 CC
  - `BaseWorkerThread`: 99 LOC, 1 CC
  - `GeocodingWorker`: 70 LOC, 1 CC
  - `WeatherDataWorker`: 248 LOC, 1 CC
  - `SQLQueryWorker`: 74 LOC, 1 CC
- **Functions:**
  - `get_optimal_data_source`: 2 LOC, 1 CC
  - `validate_api_source_available`: 2 LOC, 1 CC
  - `get_fallback_source_chain`: 2 LOC, 1 CC
  - `get_source_display_name`: 2 LOC, 1 CC
  - `log_provider_usage_event`: 2 LOC, 1 CC

### src.gui.panel_widgets.query_control_widget
- **LOC:** 898
- **Classes:** 6
- **Functions:** 1
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `HungarianLocationSelector`: 16 LOC, 1 CC
  - `DateRangeWidget`: 16 LOC, 1 CC
  - `ParametersWidget`: 13 LOC, 1 CC
  - `ProviderWidget`: 13 LOC, 1 CC
  - `QueryControlWidget`: 717 LOC, 1 CC
- **Functions:**
  - `create_query_control_widget`: 9 LOC, 1 CC

### src.gui.hungarian_location_selector
- **LOC:** 881
- **Classes:** 4
- **Functions:** 7
- **Fan-In:** 2
- **Fan-Out:** 3
- **Classes:**
  - `HungarianStatisticalRegion`: 12 LOC, 1 CC
  - `HungarianRegionData`: 13 LOC, 1 CC
  - `HungarianLocationWorker`: 44 LOC, 1 CC
  - `HungarianLocationSelector`: 675 LOC, 1 CC
- **Functions:**
  - `demo_hungarian_location_selector_with_state_management_fix`: 103 LOC, 1 CC
  - `update_debug_info`: 10 LOC, 1 CC
  - `on_region_selected`: 6 LOC, 1 CC
  - `on_county_selected`: 5 LOC, 1 CC
  - `on_location_selected`: 6 LOC, 1 CC

### src.data.weather_client
- **LOC:** 760
- **Classes:** 8
- **Functions:** 0
- **Fan-In:** 2
- **Fan-Out:** 2
- **Classes:**
  - `WeatherData`: 27 LOC, 1 CC
  - `WeatherAPIError`: 3 LOC, 1 CC
  - `ProviderNotAvailableError`: 3 LOC, 1 CC
  - `ProviderValidationError`: 3 LOC, 1 CC
  - `WeatherProvider`: 32 LOC, 1 CC

### src.gui.data_widgets
- **LOC:** 684
- **Classes:** 3
- **Functions:** 0
- **Fan-In:** 3
- **Fan-Out:** 1
- **Classes:**
  - `NumericTableWidgetItem`: 27 LOC, 1 CC
  - `WeatherTableModel`: 89 LOC, 1 CC
  - `WeatherDataTable`: 537 LOC, 1 CC

### src.gui.color_palette
- **LOC:** 677
- **Classes:** 9
- **Functions:** 7
- **Fan-In:** 6
- **Fan-Out:** 1
- **Classes:**
  - `ColorFormat`: 6 LOC, 1 CC
  - `ColorHarmony`: 8 LOC, 1 CC
  - `ColorBlindnessType`: 6 LOC, 1 CC
  - `ColorMetrics`: 8 LOC, 1 CC
  - `HSLColor`: 36 LOC, 1 CC
- **Functions:**
  - `create_color_palette`: 14 LOC, 1 CC
  - `create_material_palette`: 13 LOC, 1 CC
  - `create_weather_palette`: 17 LOC, 2 CC
  - `hex_to_hsl`: 4 LOC, 1 CC
  - `calculate_color_contrast`: 4 LOC, 1 CC

### src.gui.control_panel
- **LOC:** 658
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 9
- **Classes:**
  - `ControlPanel`: 609 LOC, 1 CC

### src.gui.dialogs.anomaly_settings_dialog
- **LOC:** 588
- **Classes:** 1
- **Functions:** 2
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `AnomalySettingsDialog`: 540 LOC, 1 CC
- **Functions:**
  - `demo_anomaly_settings_dialog`: 19 LOC, 1 CC
  - `open_dialog`: 5 LOC, 1 CC

### src.gui.results_panel.extreme_calculator
- **LOC:** 562
- **Classes:** 3
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 1
- **Classes:**
  - `ExtremeRecord`: 9 LOC, 1 CC
  - `RecordsTextSummary`: 14 LOC, 1 CC
  - `ExtremeCalculator`: 519 LOC, 1 CC

### src.gui.theme_manager
- **LOC:** 536
- **Classes:** 1
- **Functions:** 9
- **Fan-In:** 33
- **Fan-Out:** 1
- **Classes:**
  - `ProfessionalThemeManager`: 448 LOC, 1 CC
- **Functions:**
  - `get_theme_manager`: 3 LOC, 1 CC
  - `register_widget_for_theming`: 12 LOC, 2 CC
  - `apply_theme_to_app`: 3 LOC, 1 CC
  - `get_current_colors`: 3 LOC, 1 CC
  - `get_weather_colors`: 3 LOC, 1 CC

### src.gui.workers.analysis_worker
- **LOC:** 505
- **Classes:** 2
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `AnalysisWorker`: 396 LOC, 1 CC
  - `WorkerTestWindow`: 47 LOC, 1 CC

### src.gui.charts.wind_chart
- **LOC:** 491
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `WindChart`: 464 LOC, 1 CC

### src.gui.results_panel.quick_overview_tab
- **LOC:** 462
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `QuickOverviewTab`: 431 LOC, 1 CC

### src.data.anomaly_profile_manager
- **LOC:** 461
- **Classes:** 2
- **Functions:** 1
- **Fan-In:** 2
- **Fan-Out:** 0
- **Classes:**
  - `AnomalyProfileSettings`: 60 LOC, 1 CC
  - `AnomalyProfileManager`: 351 LOC, 1 CC
- **Functions:**
  - `demo_anomaly_profile_manager`: 23 LOC, 1 CC

### src.gui.universal_location_selector
- **LOC:** 456
- **Classes:** 2
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 2
- **Classes:**
  - `LocationCard`: 47 LOC, 1 CC
  - `UniversalLocationSelector`: 379 LOC, 1 CC

### src.gui.results_panel.windy_days_tab
- **LOC:** 449
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `WindyDaysTab`: 422 LOC, 1 CC

### src.gui.charts.tooltip_mixin
- **LOC:** 437
- **Classes:** 1
- **Functions:** 1
- **Fan-In:** 3
- **Fan-Out:** 1
- **Classes:**
  - `WeatherTooltipMixin`: 394 LOC, 1 CC
- **Functions:**
  - `add_tooltips_to_chart`: 16 LOC, 2 CC

### src.gui.panel_widgets.multi_city_widget
- **LOC:** 424
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 1
- **Classes:**
  - `MultiCityWidget`: 405 LOC, 1 CC

### src.analytics.multi_city_engine
- **LOC:** 417
- **Classes:** 1
- **Functions:** 7
- **Fan-In:** 10
- **Fan-Out:** 9
- **Classes:**
  - `MultiCityEngine`: 273 LOC, 1 CC
- **Functions:**
  - `safe_mean`: 3 LOC, 1 CC
  - `safe_statistics_mean`: 3 LOC, 1 CC
  - `safe_median`: 3 LOC, 1 CC
  - `safe_statistics_median`: 3 LOC, 1 CC
  - `safe_stdev`: 3 LOC, 1 CC

### src.gui.charts.temperature_chart
- **LOC:** 401
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 0
- **Fan-Out:** 3
- **Classes:**
  - `EnhancedTemperatureChart`: 377 LOC, 1 CC

### src.gui.results_panel.utils
- **LOC:** 387
- **Classes:** 3
- **Functions:** 0
- **Fan-In:** 3
- **Fan-Out:** 1
- **Classes:**
  - `WindGustsConstants`: 29 LOC, 1 CC
  - `DataFrameExtractor`: 141 LOC, 1 CC
  - `WindGustsAnalyzer`: 199 LOC, 1 CC

### src.gui.panel_widgets.date_range_widget
- **LOC:** 387
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 1
- **Classes:**
  - `DateRangeWidget`: 369 LOC, 1 CC

### src.analytics.wind_analysis
- **LOC:** 378
- **Classes:** 3
- **Functions:** 7
- **Fan-In:** 1
- **Fan-Out:** 0
- **Classes:**
  - `WindyDayStats`: 11 LOC, 1 CC
  - `WindAnalysisResult`: 11 LOC, 1 CC
  - `WindChartData`: 6 LOC, 1 CC
- **Functions:**
  - `extract_daily_wind_data`: 55 LOC, 8 CC
  - `identify_windy_days`: 27 LOC, 4 CC
  - `calculate_monthly_windy_stats`: 78 LOC, 11 CC
  - `analyze_wind_patterns`: 69 LOC, 10 CC
  - `_create_empty_analysis_result`: 14 LOC, 1 CC

### src.data.enums
- **LOC:** 364
- **Classes:** 10
- **Functions:** 12
- **Fan-In:** 13
- **Fan-Out:** 0
- **Classes:**
  - `AnalysisType`: 13 LOC, 1 CC
  - `RegionScope`: 10 LOC, 1 CC
  - `AnalyticsMetric`: 27 LOC, 1 CC
  - `QuestionType`: 24 LOC, 1 CC
  - `AnomalySeverity`: 10 LOC, 1 CC
- **Functions:**
  - `get_analysis_type_display_name`: 19 LOC, 1 CC
  - `get_data_provider_display_name`: 18 LOC, 1 CC
  - `validate_data_provider`: 9 LOC, 1 CC
  - `get_metric_display_name`: 21 LOC, 1 CC
  - `get_metric_unit`: 21 LOC, 1 CC

### src.gui.charts.heatmap_chart
- **LOC:** 361
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 2
- **Classes:**
  - `HeatmapCalendarChart`: 341 LOC, 1 CC

### src.gui.panel_widgets.provider_widget
- **LOC:** 347
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 1
- **Classes:**
  - `ProviderWidget`: 326 LOC, 1 CC

### src.gui.charts.precipitation_chart
- **LOC:** 343
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 0
- **Fan-Out:** 3
- **Classes:**
  - `PrecipitationChart`: 320 LOC, 1 CC

### src.gui.charts.windy_days_chart
- **LOC:** 337
- **Classes:** 1
- **Functions:** 2
- **Fan-In:** 1
- **Fan-Out:** 2
- **Classes:**
  - `WindyDaysChart`: 277 LOC, 1 CC
- **Functions:**
  - `create_windy_days_chart`: 9 LOC, 1 CC
  - `demo_windy_days_chart`: 33 LOC, 1 CC

### src.gui.charts.wind_rose_chart
- **LOC:** 307
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 2
- **Classes:**
  - `WindRoseChart`: 286 LOC, 1 CC

### src.gui.panel_widgets.location_widget
- **LOC:** 300
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 3
- **Classes:**
  - `LocationWidget`: 281 LOC, 1 CC

### tests.infrastructure.repositories.test_city_repository
- **LOC:** 292
- **Classes:** 0
- **Functions:** 9
- **Fan-In:** 0
- **Fan-Out:** 1
- **Functions:**
  - `create_cities_db`: 42 LOC, 2 CC
  - `create_hungarian_settlements_db`: 36 LOC, 2 CC
  - `build_repository`: 6 LOC, 1 CC
  - `test_validate_paths_raises_when_both_databases_missing`: 9 LOC, 1 CC
  - `test_validate_paths_logs_warning_when_only_hungarian_db_missing`: 13 LOC, 1 CC

### src.gui.chart_container
- **LOC:** 284
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 1
- **Fan-Out:** 2
- **Classes:**
  - `ChartsContainer`: 239 LOC, 1 CC

### src.config
- **LOC:** 264
- **Classes:** 4
- **Functions:** 6
- **Fan-In:** 5
- **Fan-Out:** 0
- **Classes:**
  - `GUIConfig`: 12 LOC, 1 CC
  - `HardwareConfig`: 7 LOC, 1 CC
  - `MultiCityConfig`: 9 LOC, 1 CC
  - `AppInfo`: 21 LOC, 1 CC
- **Functions:**
  - `check_environment`: 33 LOC, 6 CC
  - `validate_config`: 33 LOC, 6 CC
  - `get_optimal_data_source`: 16 LOC, 5 CC
  - `get_source_display_name`: 9 LOC, 1 CC
  - `validate_api_source_available`: 15 LOC, 4 CC

### src.gui.results_panel.extreme_events_tab
- **LOC:** 259
- **Classes:** 4
- **Functions:** 2
- **Fan-In:** 1
- **Fan-Out:** 7
- **Classes:**
  - `GUIConfig`: 2 LOC, 1 CC
  - `GUIConstants`: 2 LOC, 1 CC
  - `AnomalyConstants`: 2 LOC, 1 CC
  - `ExtremeEventsTab`: 185 LOC, 1 CC
- **Functions:**
  - `get_theme_manager`: 2 LOC, 1 CC
  - `register_widget_for_theming`: 2 LOC, 1 CC

### src.gui.charts.base_chart
- **LOC:** 235
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 7
- **Fan-Out:** 2
- **Classes:**
  - `WeatherChart`: 212 LOC, 1 CC

### src.gui.results_panel
- **LOC:** 231
- **Classes:** 9
- **Functions:** 3
- **Fan-In:** 3
- **Fan-Out:** 2
- **Classes:**
  - `ResultsPanel`: 5 LOC, 1 CC
  - `QuickOverviewTab`: 4 LOC, 1 CC
  - `DetailedChartsTab`: 4 LOC, 1 CC
  - `DataTableTab`: 4 LOC, 1 CC
  - `ExtremeEventsTab`: 4 LOC, 1 CC
- **Functions:**
  - `get_import_status`: 20 LOC, 1 CC
  - `validate_components`: 19 LOC, 5 CC
  - `validate_windy_days_tab`: 19 LOC, 5 CC

### meteo_gui_starter
- **LOC:** 225
- **Classes:** 1
- **Functions:** 2
- **Fan-In:** 0
- **Fan-Out:** 3
- **Classes:**
  - `WeatherAnalyzerApp`: 99 LOC, 1 CC
- **Functions:**
  - `check_requirements`: 58 LOC, 8 CC
  - `main`: 31 LOC, 4 CC

### src.config.usage_config
- **LOC:** 223
- **Classes:** 1
- **Functions:** 5
- **Fan-In:** 0
- **Fan-Out:** 3
- **Classes:**
  - `UsageTracker`: 184 LOC, 1 CC
- **Functions:**
  - `_resolve_config_attr`: 6 LOC, 3 CC
  - `_get_usage_tracking_file`: 3 LOC, 1 CC
  - `_ensure_directories`: 6 LOC, 1 CC
  - `_get_datetime_cls`: 5 LOC, 2 CC
  - `_now`: 3 LOC, 1 CC

### src.config.provider_config
- **LOC:** 196
- **Classes:** 2
- **Functions:** 6
- **Fan-In:** 1
- **Fan-Out:** 1
- **Classes:**
  - `ProviderConfig`: 46 LOC, 1 CC
  - `UserPreferences`: 88 LOC, 1 CC
- **Functions:**
  - `_resolve_config_attr`: 6 LOC, 3 CC
  - `_get_provider_prefs_file`: 3 LOC, 1 CC
  - `_ensure_directories`: 4 LOC, 1 CC
  - `_freeze_value`: 7 LOC, 3 CC
  - `get_resolved_provider`: 18 LOC, 4 CC

### src.infrastructure.repositories.city_repository
- **LOC:** 194
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 6
- **Fan-Out:** 1
- **Classes:**
  - `CityRepository`: 185 LOC, 1 CC

### src.domain.analytics.services.analytics_transform_service
- **LOC:** 194
- **Classes:** 1
- **Functions:** 0
- **Fan-In:** 2
- **Fan-Out:** 4
- **Classes:**
  - `AnalyticsTransformService`: 184 LOC, 1 CC

## 5. 🚨 Réteg Sértések (Layer Violations)

⚠️ **FIGYELEM:** 24 modul nem kategorizálható (unknown layer).
Ezek a modulok nem lesznek ellenőrizve Clean Architecture szabályok ellen.
Példák: ultimate_project_analyzer, meteo_gui_starter, src.config, src.data.anomaly_profile_manager, src.data.enums

✅ **Nem találtunk réteg sértéseket!** Clean Architecture OK.

A projekt követi a Clean Architecture Dependency Rule-t:
- Domain réteg NEM függ senkitől ✅
- Application csak Domain-től függ ✅
- Infrastructure Domain + Application-től függ ✅
- GUI Application + Infrastructure-től függ ✅

## 6. 📈 Coupling Metrics (Robert C. Martin)

**Instability (I) = Ce / (Ca + Ce)** ahol:
- **Ca** (Afferent): Bejövő függőségek száma
- **Ce** (Efferent): Kimenő függőségek száma
- **I = 0**: Maximálisan stabil (sok bejövő, nincs kimenő)
- **I = 1**: Maximálisan instabil (nincs bejövő, sok kimenő)

**Ideális állapot:**
- Domain modulok: I ≈ 0 (stabil core)
- GUI modulok: I ≈ 1 (változékony presentation)

### Top 10 Leginstabilabb Modulok

| Modul | Ca (in) | Ce (out) | Instability | Értékelés |
|-------|---------|----------|-------------|------------|
| `meteo_gui_starter` | 0 | 3 | 1.00 | ⚠️ Nagyon instabil |
| `tests.test_wind_analysis` | 0 | 1 | 1.00 | ⚠️ Nagyon instabil |
| `tests.test_weather_client_core` | 0 | 1 | 1.00 | ⚠️ Nagyon instabil |
| `tests.test_data_models` | 0 | 2 | 1.00 | ⚠️ Nagyon instabil |
| `tests.test_multi_city_engine_core` | 0 | 1 | 1.00 | ⚠️ Nagyon instabil |
| `tests.domain.test_climate_anomaly` | 0 | 1 | 1.00 | ⚠️ Nagyon instabil |
| `tests.domain.test_anomaly_threshold` | 0 | 1 | 1.00 | ⚠️ Nagyon instabil |
| `tests.domain.test_anomaly_detector_service` | 0 | 2 | 1.00 | ⚠️ Nagyon instabil |
| `tests.infrastructure.repositories.test_city_repository` | 0 | 1 | 1.00 | ⚠️ Nagyon instabil |
| `tests.domain.analytics.test_models` | 0 | 2 | 1.00 | ⚠️ Nagyon instabil |

### Top 10 Legstabilabb Modulok

| Modul | Ca (in) | Ce (out) | Instability | Értékelés |
|-------|---------|----------|-------------|------------|
| `ultimate_project_analyzer` | 0 | 0 | 0.00 | ✅ Nagyon stabil |
| `tests.test_smoke` | 0 | 0 | 0.00 | ✅ Nagyon stabil |
| `tests.test_config_core` | 0 | 0 | 0.00 | ✅ Nagyon stabil |
| `tests.test_usage_tracker_track_request` | 0 | 0 | 0.00 | ✅ Nagyon stabil |
| `tests.conftest` | 0 | 0 | 0.00 | ✅ Nagyon stabil |
| `src.config` | 5 | 0 | 0.00 | ✅ Nagyon stabil |
| `src.data.anomaly_profile_manager` | 2 | 0 | 0.00 | ✅ Nagyon stabil |
| `src.data.enums` | 13 | 0 | 0.00 | ✅ Nagyon stabil |
| `src.data` | 1 | 0 | 0.00 | ✅ Nagyon stabil |
| `src.analytics.wind_analysis` | 1 | 0 | 0.00 | ✅ Nagyon stabil |

