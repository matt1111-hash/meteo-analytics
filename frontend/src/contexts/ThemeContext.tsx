/**
 * Theme Context Provider
 * Manages theme state (light/dark) with localStorage persistence.
 * Matches PySide theme_manager functionality.
 */

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import type { ThemeType, ThemeColors, ThemeContextType } from '../types/theme';
import { THEME_STORAGE_KEY } from '../types/theme';

/**
 * Light theme colors - RED (#C43939) primary
 */
const lightColors: ThemeColors = {
  semantic: {
    primary: {
      base: '#C43939',
      light: '#D96666',
      dark: '#A32424',
      hover: '#B53030',
      pressed: '#8B1E1E',
      disabled: '#E5B8B8',
    },
    success: {
      base: '#10B981',
      light: '#34D399',
      dark: '#059669',
      hover: '#14B878',
      pressed: '#0D7A54',
      disabled: '#A7E8D6',
    },
    warning: {
      base: '#F59E0B',
      light: '#FBBF24',
      dark: '#D97706',
      hover: '#E59314',
      pressed: '#C47E06',
      disabled: '#FDE68A',
    },
    error: {
      base: '#EF4444',
      light: '#F87171',
      dark: '#DC2626',
      hover: '#F15555',
      pressed: '#D13D3D',
      disabled: '#FECACA',
    },
    info: {
      base: '#3B82F6',
      light: '#60A5FA',
      dark: '#2563EB',
      hover: '#4B91FF',
      pressed: '#1D6FE5',
      disabled: '#BDD8FE',
    },
  },
  surface: {
    background: '#F8FAFC',
    surface: '#FFFFFF',
    surfaceVariant: '#F1F5F9',
    card: '#FFFFFF',
    border: '#E2E8F0',
    divider: '#CBD5E1',
  },
  text: {
    primary: '#0F172A',
    secondary: '#475569',
    tertiary: '#64748B',
    disabled: '#94A3B8',
    inverse: '#FFFFFF',
  },
  weather: {
    hot: '#DC2626',
    warm: '#F97316',
    mild: '#EAB308',
    cool: '#22C55E',
    cold: '#06B6D4',
    freezing: '#3B82F6',
    humidity: '#8B5CF6',
    wind: '#06B6D4',
    pressure: '#6366F1',
    precipitation: '#3B82F6',
    clouds: '#94A3B8',
  },
  chart: {
    grid: '#E2E8F0',
    axis: '#94A3B8',
    tooltip: 'rgba(15, 23, 42, 0.95)',
    legend: '#475569',
  },
};

/**
 * Dark theme colors - RED adjusted for dark backgrounds
 */
const darkColors: ThemeColors = {
  semantic: {
    primary: {
      base: '#D96666',
      light: '#E08080',
      dark: '#C43939',
      hover: '#E07373',
      pressed: '#B53030',
      disabled: '#4A2323',
    },
    success: {
      base: '#22C55E',
      light: '#4ADE80',
      dark: '#16A34A',
      hover: '#2DD569',
      pressed: '#148A42',
      disabled: '#1B4D3E',
    },
    warning: {
      base: '#FBBF24',
      light: '#FCD34D',
      dark: '#F59E0B',
      hover: '#FFCA4A',
      pressed: '#E0A316',
      disabled: '#4A3D1F',
    },
    error: {
      base: '#F87171',
      light: '#FCA5A5',
      dark: '#EF4444',
      hover: '#FF8080',
      pressed: '#E05555',
      disabled: '#4A1F1F',
    },
    info: {
      base: '#60A5FA',
      light: '#93C5FD',
      dark: '#3B82F6',
      hover: '#7AB4FF',
      pressed: '#4A96E5',
      disabled: '#1E3A5F',
    },
  },
  surface: {
    background: '#0F172A',
    surface: '#1E293B',
    surfaceVariant: '#334155',
    card: '#1E293B',
    border: '#334155',
    divider: '#475569',
  },
  text: {
    primary: '#F1F5F9',
    secondary: '#CBD5E1',
    tertiary: '#94A3B8',
    disabled: '#64748B',
    inverse: '#0F172A',
  },
  weather: {
    hot: '#F87171',
    warm: '#FB923C',
    mild: '#FACC15',
    cool: '#4ADE80',
    cold: '#22D3EE',
    freezing: '#60A5FA',
    humidity: '#A78BFA',
    wind: '#22D3EE',
    pressure: '#818CF8',
    precipitation: '#60A5FA',
    clouds: '#64748B',
  },
  chart: {
    grid: '#334155',
    axis: '#64748B',
    tooltip: 'rgba(241, 245, 249, 0.95)',
    legend: '#CBD5E1',
  },
};

/**
 * Get initial theme from localStorage or system preference
 */
function getInitialTheme(): ThemeType {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored && (stored === 'light' || stored === 'dark')) {
      return stored as ThemeType;
    }
  } catch {
    // localStorage not available
  }

  // Check system preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }

  return 'light';
}

/**
 * Theme Context
 */
const ThemeContext = createContext<ThemeContextType | null>(null);

/**
 * Theme Provider Component
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemeType>(getInitialTheme);
  const [isInitialized, setIsInitialized] = useState(false);

  // Update DOM and localStorage when theme changes
  useEffect(() => {
    if (!isInitialized) {
      setIsInitialized(true);
      return;
    }

    // Update data-theme attribute on document
    document.documentElement.setAttribute('data-theme', theme);

    // Save to localStorage
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      // localStorage not available
    }

    console.log(`🎨 Theme changed to: ${theme}`);
  }, [theme, isInitialized]);

  // Initialize theme on mount (run once)
  useEffect(() => {
    const initialTheme = getInitialTheme();
    document.documentElement.setAttribute('data-theme', initialTheme);
    setThemeState(initialTheme);
    setIsInitialized(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Set theme function
  const setTheme = useCallback((newTheme: ThemeType) => {
    if (newTheme !== 'light' && newTheme !== 'dark') {
      console.warn(`Invalid theme: ${newTheme}. Use 'light' or 'dark'.`);
      return;
    }
    setThemeState(newTheme);
  }, []);

  // Toggle theme function
  const toggleTheme = useCallback(() => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  // Get colors based on current theme
  const colors = useMemo(() => {
    return theme === 'dark' ? darkColors : lightColors;
  }, [theme]);

  const contextValue = useMemo<ThemeContextType>(
    () => ({
      theme,
      colors,
      setTheme,
      toggleTheme,
    }),
    [theme, colors, setTheme, toggleTheme]
  );

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * useTheme hook
 * Usage: const { theme, colors, setTheme, toggleTheme } = useTheme();
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Helper hook to get a specific color from current theme
 */
export function useColor() {
  const { colors } = useTheme();

  return {
    primary: colors.semantic.primary.base,
    success: colors.semantic.success.base,
    warning: colors.semantic.warning.base,
    error: colors.semantic.error.base,
    info: colors.semantic.info.base,
    background: colors.surface.background,
    surface: colors.surface.surface,
    text: colors.text.primary,
    textSecondary: colors.text.secondary,
    border: colors.surface.border,
    ...colors.weather,
  };
}

/**
 * HOC to inject theme props into a component
 */
export function withTheme<P extends { theme?: ThemeType; colors?: ThemeColors }>(
  Component: React.ComponentType<P>
): React.ComponentType<Omit<P, 'theme' | 'colors'>> {
  return function ThemedComponent(props: Omit<P, 'theme' | 'colors'>) {
    const { theme, colors } = useTheme();
    return <Component {...(props as P)} theme={theme} colors={colors} />;
  };
}
