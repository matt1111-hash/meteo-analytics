#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Color Palette Module - RED THEME VERSION
🎨 KRITIKUS JAVÍTÁS: Piros (#C43939) Primary Téma hozzáadva - UNDORÍTÓ LILA ELTÁVOLÍTVA!

🎨 FŐBB FUNKCIÓK:
✅ Automatikus színvariáns generálás egyetlen base színből
✅ Semantic color mapping (primary, success, warning, error, info)
✅ HSL/HSV color space manipuláció
✅ WCAG accessibility compliance checking
✅ Color harmony generálás (complementary, triadic, analogous)
✅ Adaptive color schemes (light/dark theme optimalization)
✅ Color blindness simulation és optimization
✅ Export/import színpaletta JSON formátumban
✅ Real-time color preview generation
✅ Material Design color generator
✅ PIROS (#C43939) PRIMARY TÉMA - GYÖNYÖRŰ MEGJELENÍTÉS!

🚨 KRITIKUS JAVÍTÁS: "red" preset hozzáadva - primary: #C43939
"""

from typing import Dict, List, Tuple, Optional, NamedTuple, Union, Any
from enum import Enum
import colorsys
import math
import json
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# ABSOLUTE IMPORTS - Import hibák javítása
from src.gui.utils import ThemeType, ColorVariant


class ColorFormat(Enum):
    """Szín formátumok."""
    HEX = "hex"
    RGB = "rgb"
    HSL = "hsl"
    HSV = "hsv"


class ColorHarmony(Enum):
    """Színharmónia típusok."""
    MONOCHROMATIC = "monochromatic"
    ANALOGOUS = "analogous"
    COMPLEMENTARY = "complementary"
    TRIADIC = "triadic"
    TETRADIC = "tetradic"
    SPLIT_COMPLEMENTARY = "split_complementary"


class ColorBlindnessType(Enum):
    """Színvakság típusok szimulációhoz."""
    PROTANOPIA = "protanopia"      # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"      # Blue-blind
    ACHROMATOPSIA = "achromatopsia"  # Complete color blindness


class ColorMetrics(NamedTuple):
    """Szín metrikák accessibility ellenőrzéshez."""
    luminance: float
    contrast_ratio: float
    wcag_aa_compliant: bool
    wcag_aaa_compliant: bool
    readable_on_white: bool
    readable_on_black: bool


@dataclass
class HSLColor:
    """HSL színreprezentáció egyszerű manipulációhoz."""
    hue: float        # 0-360
    saturation: float # 0-100
    lightness: float  # 0-100
    alpha: float = 1.0    # 0-1
    
    def to_hex(self) -> str:
        """HSL konvertálás hex formátumra."""
        h, s, l = self.hue / 360, self.saturation / 100, self.lightness / 100
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    def to_rgb(self) -> Tuple[int, int, int]:
        """HSL konvertálás RGB-re."""
        h, s, l = self.hue / 360, self.saturation / 100, self.lightness / 100
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return int(r*255), int(g*255), int(b*255)
    
    def lighten(self, amount: float) -> 'HSLColor':
        """Szín világosítása amount értékkel."""
        new_lightness = min(100, self.lightness + amount)
        return HSLColor(self.hue, self.saturation, new_lightness, self.alpha)
    
    def darken(self, amount: float) -> 'HSLColor':
        """Szín sötétítése amount értékkel."""
        new_lightness = max(0, self.lightness - amount)
        return HSLColor(self.hue, self.saturation, new_lightness, self.alpha)
    
    def saturate(self, amount: float) -> 'HSLColor':
        """Szín telítettségének növelése."""
        new_saturation = min(100, self.saturation + amount)
        return HSLColor(self.hue, new_saturation, self.lightness, self.alpha)
    
    def desaturate(self, amount: float) -> 'HSLColor':
        """Szín telítettségének csökkentése."""
        new_saturation = max(0, self.saturation - amount)
        return HSLColor(self.hue, new_saturation, self.lightness, self.alpha)
    
    def rotate_hue(self, degrees: float) -> 'HSLColor':
        """Hue forgatása degrees értékkel."""
        new_hue = (self.hue + degrees) % 360
        return HSLColor(new_hue, self.saturation, self.lightness, self.alpha)


class ColorGenerator(ABC):
    """Absztrakt base class különböző színgeneráló stratégiákhoz."""
    
    @abstractmethod
    def generate_variants(self, base_color: HSLColor, theme_type: ThemeType) -> Dict[str, HSLColor]:
        """
        Színvariánsok generálása base színből.
        
        Args:
            base_color: Alapszín HSL formátumban
            theme_type: Téma típusa (light/dark)
            
        Returns:
            Színvariánsok dictionary-je
        """
        pass


class StandardColorGenerator(ColorGenerator):
    """Standard színvariáns generátor - light/dark adaptive."""
    
    def generate_variants(self, base_color: HSLColor, theme_type: ThemeType) -> Dict[str, HSLColor]:
        """Standard variánsok: light, dark, hover, pressed, disabled."""
        variants = {}
        
        if theme_type == ThemeType.LIGHT:
            # Light theme variánsok
            variants["light"] = base_color.lighten(20)
            variants["dark"] = base_color.darken(20)
            variants["hover"] = base_color.darken(10)
            variants["pressed"] = base_color.darken(30)
            variants["disabled"] = base_color.desaturate(50).lighten(30)
        else:
            # Dark theme variánsok - inverz logika
            variants["light"] = base_color.lighten(30)
            variants["dark"] = base_color.darken(15)
            variants["hover"] = base_color.lighten(15)
            variants["pressed"] = base_color.lighten(25)
            variants["disabled"] = base_color.desaturate(60).darken(20)
        
        return variants


class MaterialColorGenerator(ColorGenerator):
    """Material Design inspirált színgenerátor."""
    
    def generate_variants(self, base_color: HSLColor, theme_type: ThemeType) -> Dict[str, HSLColor]:
        """Material Design 50-900 színskála generálása."""
        variants = {}
        
        # Material Design világossági szintek
        lightness_stops = {
            "50": 95,
            "100": 90,
            "200": 80,
            "300": 70,
            "400": 60,
            "500": 50,  # Base color
            "600": 40,
            "700": 30,
            "800": 20,
            "900": 10
        }
        
        base_lightness = base_color.lightness
        
        for stop, target_lightness in lightness_stops.items():
            # Telítettség adaptálása világosság alapján
            saturation_factor = 1.0
            if target_lightness > 80:  # Very light colors
                saturation_factor = 0.6
            elif target_lightness < 20:  # Very dark colors
                saturation_factor = 0.8
            
            adjusted_saturation = base_color.saturation * saturation_factor
            variants[f"material_{stop}"] = HSLColor(
                base_color.hue,
                adjusted_saturation,
                target_lightness,
                base_color.alpha
            )
        
        # Standard variánsok hozzáadása
        variants["light"] = variants["material_200"]
        variants["dark"] = variants["material_700"]
        variants["hover"] = variants["material_400"] if theme_type == ThemeType.LIGHT else variants["material_300"]
        variants["pressed"] = variants["material_800"] if theme_type == ThemeType.LIGHT else variants["material_200"]
        variants["disabled"] = variants["material_100"] if theme_type == ThemeType.LIGHT else variants["material_800"]
        
        return variants


class ColorPalette:
    """
    🎨 Dinamikus színpaletta kezelő rendszer - PIROS TÉMA VERZIÓ.
    
    Funkciók:
    - Automatikus színvariáns generálás
    - Semantic color mapping
    - Color harmony generálás
    - Accessibility compliance checking
    - Color blindness simulation
    - Adaptive theme optimization
    - Material Design color generator
    - Professional weather app color schemes
    - 🎨 PIROS (#C43939) PRIMARY TÉMA TÁMOGATÁS!
    """
    
    def __init__(self, generator: Optional[ColorGenerator] = None):
        """
        ColorPalette inicializálása.
        
        Args:
            generator: Színgeneráló stratégia, None esetén StandardColorGenerator
        """
        self.generator = generator or StandardColorGenerator()
        self._base_colors: Dict[str, HSLColor] = {}
        self._generated_variants: Dict[str, Dict[str, HSLColor]] = {}
        self._semantic_mapping: Dict[str, str] = {}
        self._theme_type: ThemeType = ThemeType.LIGHT
        
        print("🎨 DEBUG: ColorPalette initialized - RED THEME VERSION")
    
    # === BASE COLOR MANAGEMENT ===
    
    def set_base_color(self, semantic_name: str, color: Union[str, HSLColor]) -> None:
        """
        Base szín beállítása semantic név alatt.
        
        Args:
            semantic_name: Semantic név ("primary", "success", stb.)
            color: Szín hex string vagy HSLColor formátumban
        """
        if isinstance(color, str):
            hsl_color = self._hex_to_hsl(color)
        else:
            hsl_color = color
        
        self._base_colors[semantic_name] = hsl_color
        
        # Variánsok automatikus generálása
        self._generate_variants_for_color(semantic_name)
        
        print(f"🎨 DEBUG: Base color set: {semantic_name} = {hsl_color.to_hex()}")
    
    def get_base_color(self, semantic_name: str) -> Optional[HSLColor]:
        """Base szín lekérdezése semantic név alapján."""
        return self._base_colors.get(semantic_name)
    
    def set_multiple_base_colors(self, colors: Dict[str, Union[str, HSLColor]]) -> None:
        """Több base szín egyszerre beállítása."""
        for semantic_name, color in colors.items():
            self.set_base_color(semantic_name, color)
    
    # === COLOR VARIANT ACCESS ===
    
    def get_color(self, semantic_name: str, variant: str = "base") -> Optional[str]:
        """
        Szín lekérdezése semantic név és variáns alapján.
        
        Args:
            semantic_name: Semantic név ("primary", "success", stb.)
            variant: Variáns neve ("base", "light", "dark", "hover", stb.)
            
        Returns:
            Hex színkód vagy None ha nem található
        """
        if variant == "base":
            base_color = self._base_colors.get(semantic_name)
            return base_color.to_hex() if base_color else None
        
        variants = self._generated_variants.get(semantic_name, {})
        variant_color = variants.get(variant)
        return variant_color.to_hex() if variant_color else None
    
    def get_color_hsl(self, semantic_name: str, variant: str = "base") -> Optional[HSLColor]:
        """Szín lekérdezése HSLColor formátumban."""
        if variant == "base":
            return self._base_colors.get(semantic_name)
        
        variants = self._generated_variants.get(semantic_name, {})
        return variants.get(variant)
    
    def get_all_variants(self, semantic_name: str) -> Dict[str, str]:
        """
        Összes variáns lekérdezése egy semantic névhez.
        
        Args:
            semantic_name: Semantic név
            
        Returns:
            Variánsok {variant_name: hex_color} formátumban
        """
        result = {}
        
        # Base color
        base_color = self._base_colors.get(semantic_name)
        if base_color:
            result["base"] = base_color.to_hex()
        
        # Generated variants
        variants = self._generated_variants.get(semantic_name, {})
        for variant_name, variant_color in variants.items():
            result[variant_name] = variant_color.to_hex()
        
        return result
    
    # === THEME MANAGEMENT ===
    
    def set_theme_type(self, theme_type: ThemeType) -> None:
        """
        Téma típus beállítása és variánsok újragenerálása.
        
        Args:
            theme_type: Téma típusa
        """
        if self._theme_type != theme_type:
            self._theme_type = theme_type
            
            # Összes variáns újragenerálása új téma típussal
            for semantic_name in self._base_colors.keys():
                self._generate_variants_for_color(semantic_name)
            
            print(f"🎨 DEBUG: Theme type changed to {theme_type.value}, variants regenerated")
    
    def get_theme_type(self) -> ThemeType:
        """Jelenlegi téma típus lekérdezése."""
        return self._theme_type
    
    # === SEMANTIC COLOR PRESETS ===
    
    def load_semantic_preset(self, preset_name: str) -> None:
        """
        Előre definiált semantic színkészlet betöltése.
        🎨 KRITIKUS JAVÍTÁS: "red" preset hozzáadva - primary: #C43939
        
        Args:
            preset_name: Preset neve ("default", "material", "bootstrap", "weather", "red")
        """
        presets = {
            "default": {
                "primary": "#2563eb",    # Blue
                "success": "#10b981",    # Emerald
                "warning": "#f59e0b",    # Amber
                "error": "#dc2626",      # Red
                "info": "#6b7280",       # Gray
                "surface": "#ffffff" if self._theme_type == ThemeType.LIGHT else "#1f2937",
                "background": "#f9fafb" if self._theme_type == ThemeType.LIGHT else "#111827"
            },
            "material": {
                "primary": "#1976d2",    # Material Blue
                "success": "#388e3c",    # Material Green
                "warning": "#f57c00",    # Material Orange
                "error": "#d32f2f",      # Material Red
                "info": "#1976d2",       # Material Blue
                "surface": "#ffffff" if self._theme_type == ThemeType.LIGHT else "#121212",
                "background": "#fafafa" if self._theme_type == ThemeType.LIGHT else "#000000"
            },
            "bootstrap": {
                "primary": "#0d6efd",    # Bootstrap Blue
                "success": "#198754",    # Bootstrap Green
                "warning": "#ffc107",    # Bootstrap Yellow
                "error": "#dc3545",      # Bootstrap Red
                "info": "#0dcaf0",       # Bootstrap Cyan
                "surface": "#ffffff" if self._theme_type == ThemeType.LIGHT else "#212529",
                "background": "#f8f9fa" if self._theme_type == ThemeType.LIGHT else "#000000"
            },
            "weather": {
                "primary": "#0ea5e9",    # Sky Blue
                "success": "#22c55e",    # Green
                "warning": "#eab308",    # Yellow (sun)
                "error": "#ef4444",      # Red (alert)
                "info": "#6366f1",       # Indigo
                "surface": "#ffffff" if self._theme_type == ThemeType.LIGHT else "#1e293b",
                "background": "#f1f5f9" if self._theme_type == ThemeType.LIGHT else "#0f172a"
            },
            # 🎨 KRITIKUS JAVÍTÁS: Piros (#C43939) PRIMARY TÉMA
            "red": {
                "primary": "#C43939",    # Beautiful Red (user request) 🎨
                "success": "#22c55e",    # Green
                "warning": "#f59e0b",    # Amber/Orange
                "error": "#dc2626",      # Red (darker than primary)
                "info": "#6b7280",       # Gray
                "surface": "#ffffff" if self._theme_type == ThemeType.LIGHT else "#1f2937",
                "background": "#f9fafb" if self._theme_type == ThemeType.LIGHT else "#111827"
            }
        }
        
        if preset_name in presets:
            self.set_multiple_base_colors(presets[preset_name])
            print(f"🎨 DEBUG: Semantic preset loaded: {preset_name}")
            
            # 🎨 KRITIKUS JAVÍTÁS: Piros téma alkalmazás logolása
            if preset_name == "red":
                print(f"🎨 PIROS TÉMA AKTIVÁLVA: primary = #C43939 (user request)")
        else:
            print(f"❌ DEBUG: Unknown preset: {preset_name}")
    
    # === COLOR HARMONY GENERATION ===
    
    def generate_harmony(self, base_semantic: str, harmony_type: ColorHarmony) -> Dict[str, str]:
        """
        Színharmónia generálása base szín alapján.
        
        Args:
            base_semantic: Base semantic szín neve
            harmony_type: Harmónia típusa
            
        Returns:
            Harmónia színek {name: hex_color} formátumban
        """
        base_color = self._base_colors.get(base_semantic)
        if not base_color:
            return {}
        
        harmony_colors = {}
        
        if harmony_type == ColorHarmony.COMPLEMENTARY:
            # Complementary (180° eltérés)
            comp_color = base_color.rotate_hue(180)
            harmony_colors["complementary"] = comp_color.to_hex()
            
        elif harmony_type == ColorHarmony.TRIADIC:
            # Triadic (120° eltérések)
            triadic_1 = base_color.rotate_hue(120)
            triadic_2 = base_color.rotate_hue(240)
            harmony_colors["triadic_1"] = triadic_1.to_hex()
            harmony_colors["triadic_2"] = triadic_2.to_hex()
            
        elif harmony_type == ColorHarmony.ANALOGOUS:
            # Analogous (30° eltérések)
            analog_1 = base_color.rotate_hue(30)
            analog_2 = base_color.rotate_hue(-30)
            harmony_colors["analogous_1"] = analog_1.to_hex()
            harmony_colors["analogous_2"] = analog_2.to_hex()
            
        elif harmony_type == ColorHarmony.SPLIT_COMPLEMENTARY:
            # Split complementary (150° és 210°)
            split_1 = base_color.rotate_hue(150)
            split_2 = base_color.rotate_hue(210)
            harmony_colors["split_comp_1"] = split_1.to_hex()
            harmony_colors["split_comp_2"] = split_2.to_hex()
            
        elif harmony_type == ColorHarmony.TETRADIC:
            # Tetradic/Square (90° eltérések)
            tetra_1 = base_color.rotate_hue(90)
            tetra_2 = base_color.rotate_hue(180)
            tetra_3 = base_color.rotate_hue(270)
            harmony_colors["tetradic_1"] = tetra_1.to_hex()
            harmony_colors["tetradic_2"] = tetra_2.to_hex()
            harmony_colors["tetradic_3"] = tetra_3.to_hex()
            
        elif harmony_type == ColorHarmony.MONOCHROMATIC:
            # Monochromatic (lightness variációk)
            mono_light = base_color.lighten(30)
            mono_dark = base_color.darken(30)
            mono_desat = base_color.desaturate(40)
            harmony_colors["monochromatic_light"] = mono_light.to_hex()
            harmony_colors["monochromatic_dark"] = mono_dark.to_hex()
            harmony_colors["monochromatic_muted"] = mono_desat.to_hex()
        
        print(f"🎨 DEBUG: {harmony_type.value} harmony generated from {base_semantic}")
        return harmony_colors
    
    # === ACCESSIBILITY FUNCTIONS ===
    
    def calculate_contrast_ratio(self, color1: Union[str, HSLColor], color2: Union[str, HSLColor]) -> float:
        """
        WCAG kontraszt arány számítása két szín között.
        
        Args:
            color1: Első szín
            color2: Második szín
            
        Returns:
            Kontraszt arány (1.0-21.0)
        """
        def get_luminance(color: Union[str, HSLColor]) -> float:
            if isinstance(color, str):
                hsl = self._hex_to_hsl(color)
            else:
                hsl = color
            
            r, g, b = hsl.to_rgb()
            r, g, b = r/255.0, g/255.0, b/255.0
            
            # Gamma correction
            def gamma_correct(c):
                return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)
            
            r, g, b = map(gamma_correct, [r, g, b])
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        lum1 = get_luminance(color1)
        lum2 = get_luminance(color2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def get_color_metrics(self, semantic_name: str, variant: str = "base") -> Optional[ColorMetrics]:
        """
        Szín accessibility metrikáinak lekérdezése.
        
        Args:
            semantic_name: Semantic név
            variant: Variáns neve
            
        Returns:
            ColorMetrics vagy None ha szín nem található
        """
        color = self.get_color_hsl(semantic_name, variant)
        if not color:
            return None
        
        # Luminance számítása
        r, g, b = color.to_rgb()
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Kontraszt arányok
        white_contrast = self.calculate_contrast_ratio(color, "#ffffff")
        black_contrast = self.calculate_contrast_ratio(color, "#000000")
        
        # WCAG compliance
        wcag_aa = white_contrast >= 4.5 or black_contrast >= 4.5
        wcag_aaa = white_contrast >= 7.0 or black_contrast >= 7.0
        
        return ColorMetrics(
            luminance=luminance,
            contrast_ratio=max(white_contrast, black_contrast),
            wcag_aa_compliant=wcag_aa,
            wcag_aaa_compliant=wcag_aaa,
            readable_on_white=white_contrast >= 4.5,
            readable_on_black=black_contrast >= 4.5
        )
    
    def suggest_accessible_variants(self, semantic_name: str, target_background: str) -> Dict[str, str]:
        """
        Accessible variánsok javaslása adott háttérszínhez.
        
        Args:
            semantic_name: Semantic név
            target_background: Cél háttérszín hex formátumban
            
        Returns:
            Javasolt variánsok {variant_name: hex_color}
        """
        base_color = self._base_colors.get(semantic_name)
        if not base_color:
            return {}
        
        suggestions = {}
        target_hsl = self._hex_to_hsl(target_background)
        
        # Lightness adjustment for accessibility
        if target_hsl.lightness > 50:  # Light background
            # Darker text colors needed
            for lightness in [40, 30, 20, 10]:
                variant_color = HSLColor(base_color.hue, base_color.saturation, lightness)
                contrast = self.calculate_contrast_ratio(variant_color, target_hsl)
                if contrast >= 4.5:
                    suggestions[f"accessible_dark_{lightness}"] = variant_color.to_hex()
                    break
        else:  # Dark background
            # Lighter text colors needed
            for lightness in [60, 70, 80, 90]:
                variant_color = HSLColor(base_color.hue, base_color.saturation, lightness)
                contrast = self.calculate_contrast_ratio(variant_color, target_hsl)
                if contrast >= 4.5:
                    suggestions[f"accessible_light_{lightness}"] = variant_color.to_hex()
                    break
        
        return suggestions
    
    # === COLOR BLINDNESS SIMULATION ===
    
    def simulate_color_blindness(self, semantic_name: str, blindness_type: ColorBlindnessType, variant: str = "base") -> Optional[str]:
        """
        Színvakság szimuláció adott színre.
        
        Args:
            semantic_name: Semantic név
            blindness_type: Színvakság típusa
            variant: Variáns neve
            
        Returns:
            Szimulált szín hex formátumban
        """
        color = self.get_color_hsl(semantic_name, variant)
        if not color:
            return None
        
        r, g, b = color.to_rgb()
        
        # Simplified color blindness simulation matrices
        if blindness_type == ColorBlindnessType.PROTANOPIA:
            # Red-blind simulation
            new_r = 0.567 * r + 0.433 * g
            new_g = 0.558 * r + 0.442 * g
            new_b = 0.242 * g + 0.758 * b
        elif blindness_type == ColorBlindnessType.DEUTERANOPIA:
            # Green-blind simulation
            new_r = 0.625 * r + 0.375 * g
            new_g = 0.700 * r + 0.300 * g
            new_b = 0.300 * g + 0.700 * b
        elif blindness_type == ColorBlindnessType.TRITANOPIA:
            # Blue-blind simulation
            new_r = 0.950 * r + 0.050 * g
            new_g = 0.433 * g + 0.567 * b
            new_b = 0.475 * g + 0.525 * b
        elif blindness_type == ColorBlindnessType.ACHROMATOPSIA:
            # Complete color blindness (grayscale)
            gray = 0.299 * r + 0.587 * g + 0.114 * b
            new_r = new_g = new_b = gray
        else:
            return color.to_hex()
        
        # Ensure values are in valid range
        new_r = max(0, min(255, int(new_r)))
        new_g = max(0, min(255, int(new_g)))
        new_b = max(0, min(255, int(new_b)))
        
        return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
    
    # === WEATHER-SPECIFIC COLOR METHODS ===
    
    def generate_weather_palette(self, base_temperature: str) -> Dict[str, str]:
        """
        Időjárás-specifikus színpaletta generálása hőmérséklet base színből.
        
        Args:
            base_temperature: Base hőmérséklet szín hex formátumban
            
        Returns:
            Weather színpaletta {weather_type: hex_color}
        """
        base_hsl = self._hex_to_hsl(base_temperature)
        
        weather_palette = {}
        
        # Triadic harmony alapján időjárás típusok
        weather_palette["temperature"] = base_hsl.to_hex()
        weather_palette["humidity"] = base_hsl.rotate_hue(120).to_hex()  # Kék irányba
        weather_palette["wind"] = base_hsl.rotate_hue(240).to_hex()      # Zöld irányba
        
        # Complementary alapján pressure
        weather_palette["pressure"] = base_hsl.rotate_hue(180).to_hex()
        
        # Analogous alapján precipitation
        weather_palette["precipitation"] = base_hsl.rotate_hue(60).to_hex()
        weather_palette["clouds"] = base_hsl.rotate_hue(-60).to_hex()
        
        print(f"🌦️ DEBUG: Weather palette generated from {base_temperature}")
        return weather_palette
    
    def generate_alert_gradient(self, base_alert: str, levels: int = 5) -> List[str]:
        """
        Alert szintek gradiens generálása.
        
        Args:
            base_alert: Base alert szín
            levels: Alert szintek száma
            
        Returns:
            Alert színek listája (enyhe → súlyos)
        """
        base_hsl = self._hex_to_hsl(base_alert)
        
        gradient = []
        for i in range(levels):
            # Lightness és saturation fokozatos változtatása
            factor = i / (levels - 1)  # 0.0 → 1.0
            
            lightness = base_hsl.lightness + (30 * (1 - factor))  # 70% → 40%
            saturation = base_hsl.saturation + (20 * factor)      # 60% → 80%
            
            alert_color = HSLColor(base_hsl.hue, saturation, lightness)
            gradient.append(alert_color.to_hex())
        
        print(f"🚨 DEBUG: Alert gradient generated: {levels} levels")
        return gradient
    
    # === IMPORT/EXPORT ===
    
    def export_palette(self, include_variants: bool = True) -> Dict[str, Any]:
        """
        Színpaletta exportálása JSON-kompatibilis formátumban.
        
        Args:
            include_variants: Variánsok is exportálva legyenek-e
            
        Returns:
            Export adatok
        """
        export_data = {
            "theme_type": self._theme_type.value,
            "generator_type": self.generator.__class__.__name__,
            "base_colors": {},
            "semantic_mapping": self._semantic_mapping.copy()
        }
        
        # Base colors export
        for semantic_name, hsl_color in self._base_colors.items():
            export_data["base_colors"][semantic_name] = {
                "hex": hsl_color.to_hex(),
                "hsl": {
                    "hue": hsl_color.hue,
                    "saturation": hsl_color.saturation,
                    "lightness": hsl_color.lightness,
                    "alpha": hsl_color.alpha
                }
            }
        
        # Variants export
        if include_variants:
            export_data["variants"] = {}
            for semantic_name, variants in self._generated_variants.items():
                export_data["variants"][semantic_name] = {}
                for variant_name, variant_color in variants.items():
                    export_data["variants"][semantic_name][variant_name] = variant_color.to_hex()
        
        return export_data
    
    def import_palette(self, import_data: Dict[str, Any]) -> bool:
        """
        Színpaletta importálása JSON adatokból.
        
        Args:
            import_data: Import adatok
            
        Returns:
            Sikeresen importálva-e
        """
        try:
            # Theme type
            if "theme_type" in import_data:
                self._theme_type = ThemeType(import_data["theme_type"])
            
            # Base colors
            if "base_colors" in import_data:
                for semantic_name, color_data in import_data["base_colors"].items():
                    if "hex" in color_data:
                        self.set_base_color(semantic_name, color_data["hex"])
                    elif "hsl" in color_data:
                        hsl_data = color_data["hsl"]
                        hsl_color = HSLColor(
                            hsl_data["hue"],
                            hsl_data["saturation"],
                            hsl_data["lightness"],
                            hsl_data.get("alpha", 1.0)
                        )
                        self.set_base_color(semantic_name, hsl_color)
            
            # Semantic mapping
            if "semantic_mapping" in import_data:
                self._semantic_mapping = import_data["semantic_mapping"]
            
            print("🎨 DEBUG: Palette imported successfully")
            return True
            
        except Exception as e:
            print(f"❌ DEBUG: Palette import failed: {e}")
            return False
    
    # === UTILITY METHODS ===
    
    def _hex_to_hsl(self, hex_color: str) -> HSLColor:
        """Hex szín konvertálása HSLColor-ra."""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        return HSLColor(
            hue=h * 360,
            saturation=s * 100,
            lightness=l * 100
        )
    
    def _generate_variants_for_color(self, semantic_name: str) -> None:
        """Variánsok generálása egy semantic színhez."""
        base_color = self._base_colors.get(semantic_name)
        if not base_color:
            return
        
        variants = self.generator.generate_variants(base_color, self._theme_type)
        self._generated_variants[semantic_name] = variants
        
        print(f"🎨 DEBUG: Generated {len(variants)} variants for {semantic_name}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Debug információk lekérdezése."""
        return {
            "theme_type": self._theme_type.value,
            "generator_type": self.generator.__class__.__name__,
            "base_colors_count": len(self._base_colors),
            "generated_variants_count": sum(len(variants) for variants in self._generated_variants.values()),
            "semantic_names": list(self._base_colors.keys())
        }


# === FACTORY FUNCTIONS ===

def create_color_palette(preset_name: str = "red", theme_type: ThemeType = ThemeType.LIGHT) -> ColorPalette:
    """
    🎨 KRITIKUS JAVÍTÁS: ColorPalette factory function - "red" preset alapértelmezett!
    
    Args:
        preset_name: Preset neve (alapértelmezett: "red" - #C43939)
        theme_type: Téma típusa
        
    Returns:
        Konfigurált ColorPalette instance
    """
    palette = ColorPalette()
    palette.set_theme_type(theme_type)
    palette.load_semantic_preset(preset_name)
    
    print(f"🎨 FACTORY: ColorPalette created with preset: {preset_name}")
    return palette


def create_material_palette(theme_type: ThemeType = ThemeType.LIGHT) -> ColorPalette:
    """
    Material Design ColorPalette létrehozása.
    
    Args:
        theme_type: Téma típusa
        
    Returns:
        Material Design ColorPalette
    """
    material_generator = MaterialColorGenerator()
    palette = ColorPalette(material_generator)
    palette.set_theme_type(theme_type)
    palette.load_semantic_preset("material")
    
    return palette


def create_weather_palette(base_temperature: str = "#C43939", theme_type: ThemeType = ThemeType.LIGHT) -> ColorPalette:
    """
    🎨 KRITIKUS JAVÍTÁS: Weather-specific ColorPalette - piros (#C43939) alapértelmezett!
    
    Args:
        base_temperature: Base hőmérséklet szín (alapértelmezett: #C43939)
        theme_type: Téma típusa
        
    Returns:
        Weather-optimized ColorPalette
    """
    palette = ColorPalette()
    palette.set_theme_type(theme_type)
    palette.load_semantic_preset("red")  # 🎨 KRITIKUS JAVÍTÁS: "red" preset használata
    
    # Weather-specific colors generálása
    weather_colors = palette.generate_weather_palette(base_temperature)
    for weather_type, color in weather_colors.items():
        palette.set_base_color(f"weather_{weather_type}", color)
    
    print(f"🌦️ FACTORY: Weather palette created with base temperature: {base_temperature}")
    return palette


# === GLOBAL COLOR UTILITIES ===

def hex_to_hsl(hex_color: str) -> HSLColor:
    """Convenience function hex → HSL konverzióhoz."""
    palette = ColorPalette()
    return palette._hex_to_hsl(hex_color)


def calculate_color_contrast(color1: str, color2: str) -> float:
    """Convenience function kontraszt számításhoz."""
    palette = ColorPalette()
    return palette.calculate_contrast_ratio(color1, color2)


def generate_color_variants(base_hex: str, theme_type: ThemeType = ThemeType.LIGHT) -> Dict[str, str]:
    """
    Convenience function színvariánsok generálásához.
    
    Args:
        base_hex: Base szín hex formátumban
        theme_type: Téma típusa
        
    Returns:
        Variánsok {variant_name: hex_color}
    """
    palette = ColorPalette()
    palette.set_theme_type(theme_type)
    palette.set_base_color("temp", base_hex)
    
    return palette.get_all_variants("temp")


def generate_weather_color_scheme(base_temp: str = "#C43939") -> Dict[str, str]:
    """
    🎨 KRITIKUS JAVÍTÁS: Weather color scheme - piros (#C43939) alapértelmezett!
    
    Args:
        base_temp: Base hőmérséklet szín (alapértelmezett: #C43939)
        
    Returns:
        Weather színséma
    """
    palette = ColorPalette()
    return palette.generate_weather_palette(base_temp)
