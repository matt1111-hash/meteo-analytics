# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for LayerBuilder."""

from __future__ import annotations

from .layer_builder_support import *


class LayerBuilderPart1Mixin:
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
