#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Layer Builder - Térkép layer építők.

FÁJL: src/presentation/gui/map/layer_builder.py
"""

import json
from typing import TYPE_CHECKING

try:
    import folium
    from folium import plugins

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from .map_constants import (
    COUNTY_STYLE_HIGHLIGHTED,
    COUNTY_STYLE_HOVER,
    COUNTY_STYLE_SELECTED,
)
from .map_state import FoliumMapConfig

if TYPE_CHECKING:
    import geopandas as gpd


class LayerBuilder:
    """
    🗺️ Térkép layer építő.
    """

    def __init__(self, config: FoliumMapConfig):
        """
        Args:
            config: FoliumMapConfig konfiguráció
        """
        self.config = config

    def create_base_map(self) -> "folium.Map":
        """
        🗺️ Alap Folium térkép létrehozása.

        Returns:
            folium.Map objektum
        """
        if not FOLIUM_AVAILABLE:
            raise ImportError("Folium library not available")

        # Téma alapján tiles kiválasztása
        if self.config.theme == "dark":
            tiles = "CartoDB dark_matter"
        else:
            tiles = self.config.tiles

        map_obj = folium.Map(
            location=[self.config.center_lat, self.config.center_lon],
            zoom_start=self.config.zoom_start,
            tiles=tiles,
            attr=self.config.attr,
            min_zoom=self.config.min_zoom,
            max_zoom=self.config.max_zoom,
            control_scale=True,
            prefer_canvas=True,
        )

        if self.config.disable_scroll_zoom:
            map_obj.options["scrollWheelZoom"] = False

        print(f"✅ Base Folium map created: {tiles}")
        return map_obj

    def add_counties_layer(
        self, map_obj: "folium.Map", counties_gdf: "gpd.GeoDataFrame"
    ) -> None:
        """
        🗺️ Magyar megyék GeoJSON layer hozzáadása interaktív funkcionalitással.

        Args:
            map_obj: Folium Map objektum
            counties_gdf: Megyék GeoDataFrame
        """
        if counties_gdf is None or len(counties_gdf) == 0:
            print("⚠️ No counties GeoDataFrame available")
            return

        print(f"📍 Adding {len(counties_gdf)} counties to map")

        counties_geojson = json.loads(counties_gdf.to_json())

        def style_function(feature):
            county_name = feature["properties"].get("megye", "")

            if county_name == self.config.selected_county:
                return COUNTY_STYLE_SELECTED

            if county_name in self.config.highlighted_counties:
                return COUNTY_STYLE_HIGHLIGHTED

            return {
                "fillColor": self.config.county_fill_color,
                "color": self.config.county_border_color,
                "weight": self.config.county_border_weight,
                "fillOpacity": self.config.county_fill_opacity,
            }

        def highlight_function(feature):
            return COUNTY_STYLE_HOVER

        counties_layer = folium.GeoJson(
            counties_geojson,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.Tooltip(
                folium.Html("<b>Hover a megyére a részletekért</b>", script=True),
                sticky=True,
            ),
            popup=folium.Popup(
                folium.Html("<b>Kattints a megyére</b>", script=True), max_width=200
            ),
        )

        counties_layer.add_to(map_obj)
        print("✅ Counties layer added with interactivity")

    def add_map_controls(self, map_obj: "folium.Map") -> None:
        """
        🎮 További térkép vezérlők hozzáadása.

        Args:
            map_obj: Folium Map objektum
        """
        plugins.Fullscreen().add_to(map_obj)
        plugins.MeasureControl().add_to(map_obj)
        plugins.MousePosition(
            position="bottomright",
            separator=" | ",
            empty_string="Koordináták...",
            lng_first=False,
            num_digits=20,
            prefix="Pos: ",
            lat_formatter="function(num) {return L.Util.formatNum(num, 4) + '°';}",
            lng_formatter="function(num) {return L.Util.formatNum(num, 4) + '°';}",
        ).add_to(map_obj)

        minimap = plugins.MiniMap(
            tile_layer="OpenStreetMap",
            position="bottomleft",
            width=150,
            height=150,
            collapsed_width=25,
            collapsed_height=25,
            zoom_level_offset=-5,
            zoom_animation=True,
        )
        minimap.add_to(map_obj)

        print("✅ Map controls added")

    def add_javascript_bridge(self, map_obj: "folium.Map", bridge_id: str) -> None:
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


# Export
__all__ = [
    "LayerBuilder",
]
