/**
 * Wind Constants - Beaufort Scale and wind-related utilities
 *
 * Beaufort Scale: Standard scale for wind speed based on visual observation
 * Range: 0 (Calm) to 12 (Hurricane)
 *
 * Reference: https://en.wikipedia.org/wiki/Beaufort_scale
 */

/**
 * Beaufort scale level definition
 */
export interface BeaufortLevel {
  level: number;
  name: string;
  nameHu: string;
  description: string;
  speedRange: { min: number; max: number }; // km/h
  color: string;
  icon: string;
}

/**
 * Beaufort scale levels (0-12)
 */
export const BEAUFORT_LEVELS: readonly BeaufortLevel[] = [
  {
    level: 0,
    name: 'Calm',
    nameHu: 'Szélcsend',
    description: 'Smoke rises vertically',
    speedRange: { min: 0, max: 1 },
    color: '#9ca3af', // gray
    icon: '🌫️',
  },
  {
    level: 1,
    name: 'Light Air',
    nameHu: 'Tiszta idő',
    description: 'Smoke drifts, wind vane stationary',
    speedRange: { min: 1, max: 6 },
    color: '#34d399', // light green
    icon: '🍃',
  },
  {
    level: 2,
    name: 'Light Breeze',
    nameHu: 'Enyhe szellő',
    description: 'Leaves rustle, wind felt on face',
    speedRange: { min: 6, max: 12 },
    color: '#84cc16', // lime
    icon: '🌿',
  },
  {
    level: 3,
    name: 'Gentle Breeze',
    nameHu: 'Gyenge szél',
    description: 'Leaves and small twigs in motion',
    speedRange: { min: 12, max: 20 },
    color: '#eab308', // yellow
    icon: '🍂',
  },
  {
    level: 4,
    name: 'Moderate Breeze',
    nameHu: 'Mérsékelt szél',
    description: 'Dust and loose paper raised',
    speedRange: { min: 20, max: 29 },
    color: '#fbbf24', // amber
    icon: '📰',
  },
  {
    level: 5,
    name: 'Fresh Breeze',
    nameHu: 'Élénk szél',
    description: 'Small trees in leaf begin to sway',
    speedRange: { min: 29, max: 39 },
    color: '#fb923c', // orange
    icon: '🌳',
  },
  {
    level: 6,
    name: 'Strong Breeze',
    nameHu: 'Erős szél',
    description: 'Large branches in motion, whistling heard',
    speedRange: { min: 39, max: 50 },
    color: '#f97316', // dark orange
    icon: '🌲',
  },
  {
    level: 7,
    name: 'High Wind',
    nameHu: 'Viharos szél',
    description: 'Whole trees in motion, resistance felt',
    speedRange: { min: 50, max: 62 },
    color: '#ef4444', // red
    icon: '⚠️',
  },
  {
    level: 8,
    name: 'Gale',
    nameHu: 'Szakaszos vihar',
    description: 'Twigs break off trees, difficulty walking',
    speedRange: { min: 62, max: 75 },
    color: '#dc2626', // dark red
    icon: '🌪️',
  },
  {
    level: 9,
    name: 'Strong Gale',
    nameHu: 'Erős vihar',
    description: 'Slight structural damage occurs',
    speedRange: { min: 75, max: 89 },
    color: '#b91c1c', // darker red
    icon: '🏠',
  },
  {
    level: 10,
    name: 'Storm',
    nameHu: 'Vihar',
    description: 'Trees uprooted, considerable damage',
    speedRange: { min: 89, max: 103 },
    color: '#991b1b', // blood red
    icon: '⛈️',
  },
  {
    level: 11,
    name: 'Violent Storm',
    nameHu: 'Heves vihar',
    description: 'Widespread damage, very dangerous',
    speedRange: { min: 103, max: 118 },
    color: '#7f1d1d', // deep red
    icon: '💥',
  },
  {
    level: 12,
    name: 'Hurricane',
    nameHu: 'Orkán',
    description: 'Extreme destruction, devastation',
    speedRange: { min: 118, max: 999 },
    color: '#450a0a', // maroon
    icon: '🌀',
  },
] as const;

/**
 * Get Beaufort level from wind speed in km/h
 */
export function getBeaufortLevel(speedKmh: number): BeaufortLevel {
  // Handle negative speeds as calm
  if (speedKmh < 0) {
    return BEAUFORT_LEVELS[0];
  }

  for (const level of BEAUFORT_LEVELS) {
    if (speedKmh >= level.speedRange.min && speedKmh < level.speedRange.max) {
      return level;
    }
  }
  // Fallback to hurricane for extreme speeds (>= 118)
  return BEAUFORT_LEVELS[12];
}

/**
 * Get Beaufort color for wind speed
 */
export function getBeaufortColor(speedKmh: number): string {
  return getBeaufortLevel(speedKmh).color;
}

/**
 * Format wind speed with Beaufort level indicator
 */
export function formatWindWithBeaufort(speedKmh: number): string {
  const level = getBeaufortLevel(speedKmh);
  return `${speedKmh.toFixed(1)} km/h (${level.nameHu} ${level.level})`;
}

/**
 * Wind direction labels in Hungarian
 */
export const WIND_DIRECTIONS_HU: readonly string[] = [
  'É', 'ÉK', 'K', 'DK', 'D', 'DNY', 'NY', 'ÉNY',
] as const;

/**
 * Wind direction angle mapping
 */
export const WIND_DIRECTION_ANGLES: Readonly<Record<string, number>> = {
  'N': 0,
  'NNE': 22.5,
  'NE': 45,
  'ENE': 67.5,
  'E': 90,
  'ESE': 112.5,
  'SE': 135,
  'SSE': 157.5,
  'S': 180,
  'SSW': 202.5,
  'SW': 225,
  'WSW': 247.5,
  'W': 270,
  'WNW': 292.5,
  'NW': 315,
  'NNW': 337.5,
} as const;

/**
 * Wind speed thresholds for different categories
 */
export const WIND_THRESHOLDS = {
  CALM: 1,          // km/h - End of Beaufort 0
  LIGHT: 6,         // km/h - End of Beaufort 1-2
  MODERATE: 20,     // km/h - End of Beaufort 3-4
  FRESH: 39,        // km/h - End of Beaufort 5
  STRONG: 50,       // km/h - End of Beaufort 6
  GALE: 62,         // km/h - Start of Beaufort 8
  STORM: 89,        // km/h - Start of Beaufort 10
  HURRICANE: 118,   // km/h - Start of Beaufort 12
} as const;

/**
 * Wind category for quick classification
 */
export type WindCategory =
  | 'calm'
  | 'light'
  | 'moderate'
  | 'fresh'
  | 'strong'
  | 'gale'
  | 'storm'
  | 'hurricane';

/**
 * Get wind category from speed
 */
export function getWindCategory(speedKmh: number): WindCategory {
  const beaufortLevel = getBeaufortLevel(speedKmh).level;
  if (beaufortLevel === 0) return 'calm';
  if (beaufortLevel <= 2) return 'light';
  if (beaufortLevel <= 4) return 'moderate';
  if (beaufortLevel === 5) return 'fresh';
  if (beaufortLevel <= 7) return 'strong';
  if (beaufortLevel === 8) return 'gale';
  if (beaufortLevel <= 10) return 'storm';
  return 'hurricane';
}

/**
 * Beaufort level statistics for a dataset
 */
export interface BeaufortStats {
  level: number;
  nameHu: string;
  count: number;
  percentage: number;
}

/**
 * Calculate Beaufort distribution from wind speeds
 */
export function calculateBeaufortDistribution(
  speeds: readonly number[]
): BeaufortStats[] {
  const distribution = new Map<number, number>();

  // Count occurrences per level
  for (const speed of speeds) {
    const level = getBeaufortLevel(speed).level;
    distribution.set(level, (distribution.get(level) ?? 0) + 1);
  }

  // Convert to stats array with percentages
  const total = speeds.length;
  return Array.from(distribution.entries()).map(([level, count]) => ({
    level,
    nameHu: BEAUFORT_LEVELS[level].nameHu,
    count,
    percentage: total > 0 ? (count / total) * 100 : 0,
  })).sort((a, b) => a.level - b.level);
}
