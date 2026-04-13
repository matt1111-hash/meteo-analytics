# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for LayerBuilder."""

from __future__ import annotations

from .layer_builder_support import *


class LayerBuilderPart2Mixin:  # noqa: D101
    def add_javascript_bridge(self, map_obj: folium.Map, bridge_id: str) -> None:
        """
        🌉 JavaScript bridge kód hozzáadása a térképhez.

        Args:
            map_obj: Folium Map objektum
            bridge_id: Bridge egyedi azonosító
        """
        bridge_js = f"""
        <script>
        console.log('🌉 JavaScript Bridge inicializálása...');

        var bridgeId = '{bridge_id}';
        var channel = null;
        var qtBridge = null;

        function initializeQtBridge() {{
            if (typeof qt !== 'undefined' && qt.webChannelTransport) {{
                try {{
                    new QWebChannel(qt.webChannelTransport, function(ch) {{
                        channel = ch;
                        qtBridge = channel.objects.qtBridge;
                        console.log('✅ QWebChannel bridge initialized');
                    }});
                }} catch(e) {{
                    console.log('⚠️ QWebChannel init failed:', e);
                }}
            }} else {{
                setTimeout(initializeQtBridge, 500);
            }}
        }}

        function handleCountyClick(countyName) {{
            console.log('🖱️ County clicked:', countyName);
            if (qtBridge && qtBridge.handle_county_click) {{
                qtBridge.handle_county_click(countyName);
            }}
        }}

        function handleCoordinatesClick(lat, lon) {{
            console.log('📍 Coordinates clicked:', lat, lon);
            if (qtBridge && qtBridge.handle_coordinates_click) {{
                qtBridge.handle_coordinates_click(lat, lon);
            }}
        }}

        function handleMapMove(lat, lon, zoom) {{
            console.log('🗺️ Map moved:', lat, lon, 'zoom:', zoom);
            if (qtBridge && typeof qtBridge.handle_map_move === 'function') {{
                qtBridge.handle_map_move(lat, lon, zoom);
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            console.log('📄 DOM ready, initializing bridge...');
            initializeQtBridge();

            setTimeout(function() {{
                if (typeof window.map_{map_obj._id} !== 'undefined') {{
                    var map = window.map_{map_obj._id};
                    map.on('click', function(e) {{
                        handleCoordinatesClick(e.latlng.lat, e.latlng.lng);
                    }});
                    map.on('moveend', function(e) {{
                        try {{
                            var center = map.getCenter();
                            var zoom = map.getZoom();
                            handleMapMove(center.lat, center.lng, zoom);
                        }} catch(err) {{
                            console.log('⚠️ Map move error:', err);
                        }}
                    }});
                    console.log('🗺️ Map event listeners attached');
                }} else {{
                    setTimeout(arguments.callee, 1000);
                }}
            }}, 1000);
        }});

        if (typeof QWebChannel === 'undefined') {{
            console.log('🔥 Loading QWebChannel script...');
            var script = document.createElement('script');
            script.src = 'qrc:///qtwebchannel/qwebchannel.js';
            script.onload = function() {{
                console.log('✅ QWebChannel script loaded');
                initializeQtBridge();
            }};
            script.onerror = function() {{
                console.log('⚠️ Failed to load QWebChannel script');
            }};
            document.head.appendChild(script);
        }} else {{
            initializeQtBridge();
        }}
        </script>
        """

        map_obj.get_root().html.add_child(folium.Element(bridge_js))
        print("✅ JavaScript bridge added to map")
