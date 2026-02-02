/**
 * Theme type definitions for the React frontend.
 * Matches PySide theme_manager implementation with RED (#C43939) primary.
 */

/**
 * Theme type - light or dark mode
 */
export type ThemeType = 'light' | 'dark';

/**
 * Semantic color variants for each color
 */
export interface ColorVariants {
  base: string;
  light: string;
  dark: string;
  hover: string;
  pressed: string;
  disabled: string;
}

/**
 * Semantic colors matching PySide ColorPalette
 */
export interface SemanticColors {
  primary: ColorVariants;
  success: ColorVariants;
  warning: ColorVariants;
  error: ColorVariants;
  info: ColorVariants;
}

/**
 * Surface colors for backgrounds, cards, etc.
 */
export interface SurfaceColors {
  background: string;
  surface: string;
  surfaceVariant: string;
  card: string;
  border: string;
  divider: string;
}

/**
 * Text colors with WCAG compliance
 */
export interface TextColors {
  primary: string;
  secondary: string;
  tertiary: string;
  disabled: string;
  inverse: string;
}

/**
 * Weather-specific colors matching PySide weather palette
 */
export interface WeatherColors {
  hot: string;        // Extreme heat
  warm: string;       // Warm temperature
  mild: string;       // Mild/pleasant
  cool: string;       // Cool temperature
  cold: string;       // Cold temperature
  freezing: string;   // Freezing/extreme cold
  humidity: string;   // Humidity indicator
  wind: string;       // Wind speed
  pressure: string;   // Atmospheric pressure
  precipitation: string; // Rain/snow
  clouds: string;     // Cloud cover
}

/**
 * Complete theme color set
 */
export interface ThemeColors {
  semantic: SemanticColors;
  surface: SurfaceColors;
  text: TextColors;
  weather: WeatherColors;
  chart: {
    grid: string;
    axis: string;
    tooltip: string;
    legend: string;
  };
}

/**
 * Theme context type
 */
export interface ThemeContextType {
  theme: ThemeType;
  colors: ThemeColors;
  setTheme: (theme: ThemeType) => void;
  toggleTheme: () => void;
}

/**
 * Local storage key for theme persistence
 */
export const THEME_STORAGE_KEY = 'meteo-analytics-theme';
