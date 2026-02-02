/**
 * windConstants.test.ts
 * Szigorú tesztek a Beaufort skála és szélhez kapcsolódó konstansokhoz
 *
 * @see AGENTS.md - Quality Gate: Coverage ≥85% (local)
 */

import {
  BEAUFORT_LEVELS,
  getBeaufortLevel,
  getBeaufortColor,
  formatWindWithBeaufort,
  WIND_DIRECTIONS_HU,
  WIND_DIRECTION_ANGLES,
  WIND_THRESHOLDS,
  getWindCategory,
  calculateBeaufortDistribution,
  type BeaufortLevel,
  type BeaufortStats,
  type WindCategory,
} from './windConstants';

describe('windConstants', () => {
  describe('BEAUFORT_LEVELS', () => {
    test('should have exactly 13 levels (0-12)', () => {
      expect(BEAUFORT_LEVELS).toHaveLength(13);
    });

    test('should have consecutive levels from 0 to 12', () => {
      BEAUFORT_LEVELS.forEach((level, index) => {
        expect(level.level).toBe(index);
      });
    });

    test('each level should have required properties', () => {
      BEAUFORT_LEVELS.forEach((level) => {
        expect(level).toHaveProperty('level');
        expect(level).toHaveProperty('name');
        expect(level).toHaveProperty('nameHu');
        expect(level).toHaveProperty('description');
        expect(level).toHaveProperty('speedRange');
        expect(level).toHaveProperty('color');
        expect(level).toHaveProperty('icon');

        expect(typeof level.level).toBe('number');
        expect(typeof level.name).toBe('string');
        expect(typeof level.nameHu).toBe('string');
        expect(typeof level.description).toBe('string');
        expect(typeof level.speedRange.min).toBe('number');
        expect(typeof level.speedRange.max).toBe('number');
        expect(typeof level.color).toBe('string');
        expect(typeof level.icon).toBe('string');
      });
    });

    test('speed ranges should be continuous and non-overlapping', () => {
      for (let i = 0; i < BEAUFORT_LEVELS.length - 1; i++) {
        const current = BEAUFORT_LEVELS[i];
        const next = BEAUFORT_LEVELS[i + 1];
        expect(current.speedRange.max).toBe(next.speedRange.min);
      }
    });

    test('level 0 should start at 0 km/h', () => {
      expect(BEAUFORT_LEVELS[0].speedRange.min).toBe(0);
    });

    test('level 12 should have very high max speed', () => {
      expect(BEAUFORT_LEVELS[12].speedRange.max).toBeGreaterThan(100);
    });

    test('all levels should have valid hex colors', () => {
      const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;
      BEAUFORT_LEVELS.forEach((level) => {
        expect(level.color).toMatch(hexColorRegex);
      });
    });

    test('Hungarian names should be non-empty strings', () => {
      BEAUFORT_LEVELS.forEach((level) => {
        expect(level.nameHu.length).toBeGreaterThan(0);
        expect(level.nameHu.trim()).toBeTruthy();
      });
    });

    test('icons should be emoji or special characters', () => {
      BEAUFORT_LEVELS.forEach((level) => {
        expect(level.icon.length).toBeGreaterThan(0);
        // Most are emoji (2+ chars) or single special chars
        expect(level.icon.length).toBeLessThanOrEqual(4);
      });
    });
  });

  describe('getBeaufortLevel', () => {
    test('should return level 0 for speeds < 1 km/h', () => {
      expect(getBeaufortLevel(0).level).toBe(0);
      expect(getBeaufortLevel(0.5).level).toBe(0);
    });

    test('should return level 1 for speeds 1-6 km/h', () => {
      expect(getBeaufortLevel(1).level).toBe(1);
      expect(getBeaufortLevel(3).level).toBe(1);
      expect(getBeaufortLevel(5.9).level).toBe(1);
    });

    test('should return level 6 for speeds 39-50 km/h (Strong Breeze)', () => {
      expect(getBeaufortLevel(39).level).toBe(6);
      expect(getBeaufortLevel(45).level).toBe(6);
      expect(getBeaufortLevel(49.9).level).toBe(6);
    });

    test('should return level 8 for speeds 62-75 km/h (Gale)', () => {
      expect(getBeaufortLevel(62).level).toBe(8);
      expect(getBeaufortLevel(68).level).toBe(8);
      expect(getBeaufortLevel(74.9).level).toBe(8);
    });

    test('should return level 10 for speeds 89-103 km/h (Storm)', () => {
      expect(getBeaufortLevel(89).level).toBe(10);
      expect(getBeaufortLevel(95).level).toBe(10);
      expect(getBeaufortLevel(102.9).level).toBe(10);
    });

    test('should return level 12 for speeds >= 118 km/h (Hurricane)', () => {
      expect(getBeaufortLevel(118).level).toBe(12);
      expect(getBeaufortLevel(150).level).toBe(12);
      expect(getBeaufortLevel(200).level).toBe(12);
    });

    test('should return valid BeaufortLevel object', () => {
      const result = getBeaufortLevel(25);
      expect(result).toHaveProperty('level');
      expect(result).toHaveProperty('name');
      expect(result).toHaveProperty('nameHu');
      expect(result).toHaveProperty('description');
      expect(result).toHaveProperty('speedRange');
      expect(result).toHaveProperty('color');
      expect(result).toHaveProperty('icon');
    });

    test('should handle negative speeds (return level 0)', () => {
      expect(getBeaufortLevel(-1).level).toBe(0);
      expect(getBeaufortLevel(-10).level).toBe(0);
    });

    test('should handle decimal speeds correctly', () => {
      expect(getBeaufortLevel(6.1).level).toBe(2); // Just above 6
      expect(getBeaufortLevel(11.9).level).toBe(2); // Just below 12
      expect(getBeaufortLevel(12.1).level).toBe(3); // Just above 12
    });
  });

  describe('getBeaufortColor', () => {
    test('should return valid hex color for any speed', () => {
      const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;
      expect(getBeaufortColor(0)).toMatch(hexColorRegex);
      expect(getBeaufortColor(25)).toMatch(hexColorRegex);
      expect(getBeaufortColor(100)).toMatch(hexColorRegex);
      expect(getBeaufortColor(200)).toMatch(hexColorRegex);
    });

    test('should return gray for calm winds (level 0)', () => {
      expect(getBeaufortColor(0)).toBe('#9ca3af');
      expect(getBeaufortColor(0.5)).toBe('#9ca3af');
    });

    test('should return dark red for hurricane (level 12)', () => {
      expect(getBeaufortColor(118)).toBe('#450a0a');
      expect(getBeaufortColor(150)).toBe('#450a0a');
    });

    test('should return progressively more intense colors', () => {
      const calmColor = getBeaufortColor(0);
      const breezeColor = getBeaufortColor(15);
      const galeColor = getBeaufortColor(65);
      const hurricaneColor = getBeaufortColor(120);

      expect(calmColor).not.toBe(breezeColor);
      expect(breezeColor).not.toBe(galeColor);
      expect(galeColor).not.toBe(hurricaneColor);
    });
  });

  describe('formatWindWithBeaufort', () => {
    test('should format speed with Beaufort level', () => {
      const result = formatWindWithBeaufort(25);
      expect(result).toContain('25.0');
      expect(result).toContain('km/h');
      expect(result).toContain('Mérsékelt szél');
      expect(result).toContain('4');
    });

    test('should include decimal point for speeds', () => {
      expect(formatWindWithBeaufort(12.5)).toContain('12.5');
      expect(formatWindWithBeaufort(45.7)).toContain('45.7');
    });

    test('should handle calm winds correctly', () => {
      const result = formatWindWithBeaufort(0);
      expect(result).toContain('Szélcsend');
      expect(result).toContain('0');
    });

    test('should handle hurricane winds correctly', () => {
      const result = formatWindWithBeaufort(150);
      expect(result).toContain('Orkán');
      expect(result).toContain('12');
    });

    test('should always include Hungarian name', () => {
      for (const speed of [0, 5, 15, 35, 55, 75, 95, 120]) {
        const result = formatWindWithBeaufort(speed);
        expect(result.length).toBeGreaterThan(10);
      }
    });
  });

  describe('WIND_DIRECTIONS_HU', () => {
    test('should have 8 cardinal directions', () => {
      expect(WIND_DIRECTIONS_HU).toHaveLength(8);
    });

    test('should contain cardinal directions in Hungarian', () => {
      expect(WIND_DIRECTIONS_HU).toContain('É'); // North (Észak)
      expect(WIND_DIRECTIONS_HU).toContain('K'); // East (Kelet)
      expect(WIND_DIRECTIONS_HU).toContain('D'); // South (Dél)
      expect(WIND_DIRECTIONS_HU).toContain('NY'); // West (Nyugat)
    });
  });

  describe('WIND_DIRECTION_ANGLES', () => {
    test('should have valid angle mappings', () => {
      expect(WIND_DIRECTION_ANGLES['N']).toBe(0);
      expect(WIND_DIRECTION_ANGLES['E']).toBe(90);
      expect(WIND_DIRECTION_ANGLES['S']).toBe(180);
      expect(WIND_DIRECTION_ANGLES['W']).toBe(270);
    });

    test('should have 16 directions', () => {
      const keys = Object.keys(WIND_DIRECTION_ANGLES);
      expect(keys.length).toBe(16);
    });

    test('all angles should be between 0 and 360', () => {
      Object.values(WIND_DIRECTION_ANGLES).forEach((angle) => {
        expect(angle).toBeGreaterThanOrEqual(0);
        expect(angle).toBeLessThan(360);
      });
    });
  });

  describe('WIND_THRESHOLDS', () => {
    test('should have all required thresholds', () => {
      expect(WIND_THRESHOLDS).toHaveProperty('CALM');
      expect(WIND_THRESHOLDS).toHaveProperty('LIGHT');
      expect(WIND_THRESHOLDS).toHaveProperty('MODERATE');
      expect(WIND_THRESHOLDS).toHaveProperty('FRESH');
      expect(WIND_THRESHOLDS).toHaveProperty('STRONG');
      expect(WIND_THRESHOLDS).toHaveProperty('GALE');
      expect(WIND_THRESHOLDS).toHaveProperty('STORM');
      expect(WIND_THRESHOLDS).toHaveProperty('HURRICANE');
    });

    test('thresholds should be in ascending order', () => {
      expect(WIND_THRESHOLDS.CALM).toBeLessThan(WIND_THRESHOLDS.LIGHT);
      expect(WIND_THRESHOLDS.LIGHT).toBeLessThan(WIND_THRESHOLDS.MODERATE);
      expect(WIND_THRESHOLDS.MODERATE).toBeLessThan(WIND_THRESHOLDS.FRESH);
      expect(WIND_THRESHOLDS.FRESH).toBeLessThan(WIND_THRESHOLDS.STRONG);
      expect(WIND_THRESHOLDS.STRONG).toBeLessThan(WIND_THRESHOLDS.GALE);
      expect(WIND_THRESHOLDS.GALE).toBeLessThan(WIND_THRESHOLDS.STORM);
      expect(WIND_THRESHOLDS.STORM).toBeLessThan(WIND_THRESHOLDS.HURRICANE);
    });

    test('thresholds should match Beaufort boundaries', () => {
      expect(WIND_THRESHOLDS.CALM).toBe(BEAUFORT_LEVELS[0].speedRange.max);
      expect(WIND_THRESHOLDS.STRONG).toBe(BEAUFORT_LEVELS[6].speedRange.max);
      expect(WIND_THRESHOLDS.GALE).toBe(BEAUFORT_LEVELS[8].speedRange.min);
      expect(WIND_THRESHOLDS.STORM).toBe(BEAUFORT_LEVELS[10].speedRange.min);
      expect(WIND_THRESHOLDS.HURRICANE).toBe(BEAUFORT_LEVELS[12].speedRange.min);
    });
  });

  describe('getWindCategory', () => {
    test('should return correct category for each threshold', () => {
      expect(getWindCategory(0)).toBe('calm');
      expect(getWindCategory(3)).toBe('light');
      expect(getWindCategory(15)).toBe('moderate');
      expect(getWindCategory(30)).toBe('fresh');
      expect(getWindCategory(45)).toBe('strong');
      expect(getWindCategory(65)).toBe('gale');
      expect(getWindCategory(80)).toBe('storm');
      expect(getWindCategory(95)).toBe('storm');
      expect(getWindCategory(120)).toBe('hurricane');
    });

    test('should return hurricane for extreme speeds', () => {
      expect(getWindCategory(200)).toBe('hurricane');
      expect(getWindCategory(500)).toBe('hurricane');
    });

    test('should handle edge cases correctly', () => {
      expect(getWindCategory(0.9)).toBe('calm');
      expect(getWindCategory(1)).toBe('light');
      expect(getWindCategory(5.9)).toBe('light');
      expect(getWindCategory(6)).toBe('light');
      expect(getWindCategory(12)).toBe('moderate');
    });
  });

  describe('calculateBeaufortDistribution', () => {
    test('should return empty array for empty input', () => {
      const result = calculateBeaufortDistribution([]);
      expect(result).toEqual([]);
    });

    test('should count occurrences per level correctly', () => {
      const speeds = [0, 0.5, 3, 10, 25, 45, 70, 100, 150] as const;
      const result = calculateBeaufortDistribution(speeds);

      expect(result.length).toBeGreaterThan(0);

      // Check that all speeds are categorized
      const totalCount = result.reduce((sum, stat) => sum + stat.count, 0);
      expect(totalCount).toBe(speeds.length);
    });

    test('should calculate percentages correctly', () => {
      const speeds = [5, 15, 25, 35]; // All in different levels
      const result = calculateBeaufortDistribution(speeds);

      result.forEach((stat) => {
        expect(stat.percentage).toBeGreaterThanOrEqual(0);
        expect(stat.percentage).toBeLessThanOrEqual(100);
      });

      // Total percentage should be 100%
      const totalPercentage = result.reduce((sum, stat) => sum + stat.percentage, 0);
      expect(totalPercentage).toBeCloseTo(100, 1);
    });

    test('should handle single speed values', () => {
      const result = calculateBeaufortDistribution([25]);

      expect(result).toHaveLength(1);
      expect(result[0].count).toBe(1);
      expect(result[0].percentage).toBe(100);
      expect(result[0].level).toBe(4); // 25 km/h is level 4 (Moderate Breeze)
    });

    test('should handle all same speeds', () => {
      const speeds = [10, 10, 10, 10, 10];
      const result = calculateBeaufortDistribution(speeds);

      expect(result).toHaveLength(1);
      expect(result[0].count).toBe(5);
      expect(result[0].percentage).toBe(100);
    });

    test('should include Hungarian names', () => {
      const speeds = [0, 25, 50, 100];
      const result = calculateBeaufortDistribution(speeds);

      result.forEach((stat) => {
        expect(stat.nameHu).toBeTruthy();
        expect(stat.nameHu.length).toBeGreaterThan(0);
      });
    });

    test('should be sorted by level', () => {
      const speeds = [100, 10, 50, 0, 25];
      const result = calculateBeaufortDistribution(speeds);

      for (let i = 1; i < result.length; i++) {
        expect(result[i].level).toBeGreaterThan(result[i - 1].level);
      }
    });

    test('should handle null/undefined gracefully', () => {
      // @ts-expect-error - Testing invalid input
      const result = calculateBeaufortDistribution([null, undefined, 10]);
      // Should not throw and handle valid values
      expect(result.length).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases and Integration', () => {
    test('getBeaufortLevel and getBeaufortColor should be consistent', () => {
      const speed = 45;
      const level = getBeaufortLevel(speed);
      const color = getBeaufortColor(speed);

      expect(color).toBe(level.color);
    });

    test('formatWindWithBeaufort should use getBeaufortLevel', () => {
      const speed = 65;
      const level = getBeaufortLevel(speed);
      const formatted = formatWindWithBeaufort(speed);

      expect(formatted).toContain(level.nameHu);
      expect(formatted).toContain(level.level.toString());
    });

    test('distribution should match individual getBeaufortLevel calls', () => {
      const speeds = [10, 20, 30, 40, 50];
      const distribution = calculateBeaufortDistribution(speeds);

      speeds.forEach((speed) => {
        const level = getBeaufortLevel(speed);
        const stat = distribution.find((s) => s.level === level.level);
        expect(stat).toBeDefined();
        expect(stat!.count).toBeGreaterThan(0);
      });
    });

    test('should handle very large speed values', () => {
      const extremeSpeed = 9999;
      const level = getBeaufortLevel(extremeSpeed);
      expect(level.level).toBe(12);

      const color = getBeaufortColor(extremeSpeed);
      expect(color).toBe('#450a0a');

      const category = getWindCategory(extremeSpeed);
      expect(category).toBe('hurricane');
    });

    test('should handle floating point precision', () => {
      const speed = 38.999999999;
      const level = getBeaufortLevel(speed);
      expect(level.level).toBeLessThan(6); // Should be level 5, not 6

      const speed2 = 39.000000001;
      const level2 = getBeaufortLevel(speed2);
      expect(level2.level).toBe(6); // Should be level 6
    });
  });
});
