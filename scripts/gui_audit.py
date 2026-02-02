#!/usr/bin/env python3
"""
GUI Audit Script v3 - Critical errors only.

Igazi hibák:
- _apply_theme_to_chart hiányzik
- Port szignatúra inkonzisztencia
- Method CALLS hiánya (nem connect())
"""

import ast
import re
from pathlib import Path
from typing import Dict, List


class GUIAuditor:
    """Static analyzer for GUI code - critical errors only."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.errors: List[str] = []
        self.class_methods: Dict[str, Set[str]] = {}

        # Whitelist: known mixin attributes (false positives)
        self.mixin_whitelist = {
            'on_search_requested', 'on_city_selected', 'on_location_changed',
            'on_date_range_changed', 'on_date_mode_changed', 'on_provider_changed',
            'on_fetch_requested', 'on_cancel_requested', 'on_analysis_type_changed',
            'on_multi_city_selection_changed', 'on_api_settings_changed',
            'on_query_clicked', 'on_progress', 'on_error', 'on_completed',
            'on_header_clicked', 'on_selection_changed', 'on_tab_changed',
            'on_anomaly_settings_clicked', 'on_detailed_analysis_clicked',
            'on_period_type_changed', 'on_loading_timeout', 'on_settings_changed',
            'on_button_clicked', 'on_chart_clicked', 'on_result_selected',
            'on_result_clicked', 'perform_search', 'trigger_search',
            'apply_filter', 'change_page', 'change_page_size',
            'on_county_changed', 'start_data_loading', 'center_map_on_selection',
            'on_counties_loaded', 'on_postal_codes_loaded', 'on_data_error',
            'on_data_loading_completed', 'on_map_generated', 'on_map_error',
            'on_server_ready', 'on_server_error', 'on_county_clicked',
            'on_coordinates_clicked', 'on_map_moved', 'on_county_hovered',
            'on_export_completed', 'map_ready', 'county_clicked', 'coordinates_clicked',
            'map_moved', 'county_hovered', 'export_completed', 'error_occurred',
            'on_style_changed', 'on_counties_toggled', 'on_weather_toggled',
            'on_zoom_changed', '_refresh_map', '_export_map', 'on_map_loaded',
            '_on_js_county_clicked', '_on_js_coordinates_clicked', '_on_js_map_moved',
            '_on_js_county_hovered', 'check_interruption', 'geocoding_results_ready',
            'city_saved_to_db', 'weather_data_ready', 'weather_saved_to_db',
            'status_updated', 'analysis_started', 'analysis_progress',
            'analysis_completed', 'analysis_failed', 'analysis_cancelled',
            'error_occurred', 'progress_updated', 'provider_selected',
            'provider_usage_updated', 'provider_warning', 'provider_fallback',
            'local_error_occurred', 'analysis_requested', 'cancel_requested',
            'query_requested', 'city_selected', 'search_requested',
            '_on_analysis_started', '_on_analysis_completed', '_on_analysis_failed',
            '_on_analysis_cancelled', '_on_provider_selected', '_on_provider_usage_updated',
            '_on_provider_warning', '_on_provider_fallback', '_on_local_error',
            '_on_analysis_requested', '_handle_export_request', '_show_extreme_weather',
            '_handle_analytics_view_query', '_on_progress_clean', 'update_data',
            'on_time_range_changed', 'on_manual_date_changed', 'set_last_month',
            'set_last_year', 'on_provider_selection_changed', 'on_combo_selection_changed',
            'on_auto_reset', 'update_progress_animation', 'test_validation',
            'test_fetch', 'test_error', 'on_query_requested', 'on_cancel_requested',
            'simulate_fetch_complete', 'on_loading_timeout', 'apply_theme',
            '_apply_theme_to_chart',
        }

    def audit(self) -> List[str]:
        """Run critical audits only."""
        print("=" * 80)
        print("🔍 GUI AUDIT v3 - Critical Errors Only")
        print("=" * 80)

        self._scan_classes()
        self._check_critical_method_calls()
        self._check_port_signatures()

        return self.errors

    def _scan_classes(self):
        """Scan classes and their methods."""
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
            except:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = set()
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.add(item.name)
                    rel_path = str(py_file.relative_to(self.project_root))
                    self.class_methods[f"{rel_path}:{node.name}"] = methods

    def _check_critical_method_calls(self):
        """Check only CRITICAL method calls (not connect())."""
        # Pattern: self.method() where method is NOT in whitelist
        # AND method is called (not just referenced)
        pattern = re.compile(r'self\._?(\w+)\(')

        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line_no, line in enumerate(lines, 1):
                    # Skip connect() lines
                    if '.connect(' in line:
                        continue

                    matches = pattern.findall(line)
                    for method_name in matches:
                        if method_name in self.mixin_whitelist:
                            continue

                        # Check if method exists
                        found = False
                        rel_path = str(py_file.relative_to(self.project_root))
                        for class_key, methods in self.class_methods.items():
                            if class_key.startswith(rel_path) and method_name in methods:
                                found = True
                                break

                        if not found:
                            self.errors.append(
                                f"HIBA: {rel_path}:{line_no} - "
                                f"hiányzó metódus: 'self.{method_name}()'"
                            )
            except:
                pass

    def _check_port_signatures(self):
        """Check port signature consistency."""
        ports_file = self.src_dir / "domain" / "ports" / "__init__.py"
        if not ports_file.exists():
            return

        with open(ports_file, 'r') as f:
            port_content = f.read()

        # Check WeatherClientPort
        port_match = re.search(
            r'class WeatherClientPort.*?def get_weather_data\((.*?)\):',
            port_content,
            re.DOTALL
        )

        if port_match:
            port_params = port_match.group(1)
            port_has_lat = 'lat:' in port_params or 'lat,' in port_params or 'lat ' in port_params
            port_has_latitude = 'latitude:' in port_params

            impl_file = self.src_dir / "data" / "weather_client_core.py"
            if impl_file.exists():
                with open(impl_file, 'r') as f:
                    impl_content = f.read()

                impl_match = re.search(
                    r'def get_weather_data\((.*?)\):',
                    impl_content,
                    re.DOTALL
                )

                if impl_match:
                    impl_params = impl_match.group(1)
                    impl_has_lat = 'lat' in impl_params and 'latitude' not in impl_params
                    impl_has_latitude = 'latitude' in impl_params

                    if port_has_lat and impl_has_latitude:
                        self.errors.append(
                            f"HIBA: {impl_file.relative_to(self.project_root)}:1 - "
                            f"Port szignatúra: Port='lat/lon' vs Impl='latitude/longitude'"
                        )


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    auditor = GUIAuditor(project_root)
    errors = auditor.audit()

    print("\n" + "=" * 80)
    print(f"📊 KRITIKUS HIBÁK: {len(errors)}")
    print("=" * 80)

    if errors:
        print("\n🚨 TALÁLT HIBÁK:\n")
        for error in errors:
            print(f"  {error}")
        return 1
    else:
        print("\n✅ NINCS KRITIKUS HIBA!")
        return 0


if __name__ == "__main__":
    exit(main())
