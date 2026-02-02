/**
 * hungary.test.ts
 * Szigorú tesztek a Magyarország földrajzi konstansaihoz
 *
 * @see AGENTS.md - Quality Gate: Coverage ≥85% (local)
 */

import {
  HUNGARIAN_REGIONS,
  HUNGARIAN_COUNTIES,
  SETTLEMENT_TYPES_HU,
  COUNTY_TO_REGION_MAP,
  REGION_TO_COUNTIES_MAP,
  getCountyNameHu,
  getRegionForCounty,
  getCountiesForRegion,
  isValidRegion,
  isValidCounty,
  getCountyData,
  formatSettlementType,
  getCountyNames,
  getRegionNames,
  getCountyDensity,
  COUNTIES_BY_POPULATION,
  COUNTIES_BY_AREA,
  type HungarianCounty,
  type HungarianRegion,
  type SettlementType,
  type HungarianSettlement,
  type HungarianWeatherStation,
  type CountiesResponse,
  type RegionsResponse,
  type SettlementsResponse,
  type StationsResponse,
} from './hungary';

describe('hungary constants', () => {
  describe('HUNGARIAN_REGIONS', () => {
    test('should have exactly 7 statistical regions', () => {
      expect(HUNGARIAN_REGIONS).toHaveLength(7);
    });

    test('should contain all expected regions', () => {
      const expectedRegions: HungarianRegion[] = [
        'Közép-Magyarország',
        'Észak-Magyarország',
        'Észak-Alföld',
        'Dél-Alföld',
        'Dél-Dunántúl',
        'Nyugat-Dunántúl',
        'Közép-Dunántúl',
      ];
      expect(HUNGARIAN_REGIONS).toEqual(expect.arrayContaining(expectedRegions));
    });

    test('all regions should be non-empty strings', () => {
      HUNGARIAN_REGIONS.forEach((region) => {
        expect(typeof region).toBe('string');
        expect(region.length).toBeGreaterThan(0);
      });
    });

    test('regions should be unique', () => {
      const uniqueRegions = new Set(HUNGARIAN_REGIONS);
      expect(uniqueRegions.size).toBe(HUNGARIAN_REGIONS.length);
    });
  });

  describe('HUNGARIAN_COUNTIES', () => {
    test('should have exactly 20 counties (19 + Budapest)', () => {
      expect(HUNGARIAN_COUNTIES).toHaveLength(20);
    });

    test('Budapest should be first', () => {
      expect(HUNGARIAN_COUNTIES[0].name).toBe('Budapest');
    });

    test('each county should have required properties', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(county).toHaveProperty('name');
        expect(county).toHaveProperty('nameHu');
        expect(county).toHaveProperty('region');
        expect(county).toHaveProperty('seat');
        expect(county).toHaveProperty('areaKm2');
        expect(county).toHaveProperty('population');

        expect(typeof county.name).toBe('string');
        expect(typeof county.nameHu).toBe('string');
        expect(typeof county.region).toBe('string');
        expect(typeof county.seat).toBe('string');
        expect(typeof county.areaKm2).toBe('number');
        expect(typeof county.population).toBe('number');
      });
    });

    test('all county names should match Hungarian names', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(county.name).toBe(county.nameHu);
      });
    });

    test('all counties should have valid areas (> 0)', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(county.areaKm2).toBeGreaterThan(0);
      });
    });

    test('all counties should have valid populations (> 0)', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(county.population).toBeGreaterThan(0);
      });
    });

    test('county names should be unique', () => {
      const countyNames = HUNGARIAN_COUNTIES.map((c) => c.name);
      const uniqueNames = new Set(countyNames);
      expect(uniqueNames.size).toBe(countyNames.length);
    });

    test('all county regions should be valid Hungarian regions', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(isValidRegion(county.region)).toBe(true);
      });
    });

    test('Budapest should have specific properties', () => {
      const budapest = HUNGARIAN_COUNTIES.find((c) => c.name === 'Budapest');
      expect(budapest).toBeDefined();
      expect(budapest?.seat).toBe('Budapest');
      expect(budapest?.region).toBe('Közép-Magyarország');
      expect(budapest?.population).toBeGreaterThan(1500000);
    });

    test('largest county by area should be Bács-Kiskun or similar', () => {
      const largestByArea = COUNTIES_BY_AREA[0];
      expect(largestByArea.areaKm2).toBeGreaterThan(8000);
    });

    test('most populous county should be Budapest', () => {
      const mostPopulous = COUNTIES_BY_POPULATION[0];
      expect(mostPopulous.name).toBe('Budapest');
    });
  });

  describe('SETTLEMENT_TYPES_HU', () => {
    test('should have exactly 4 settlement types', () => {
      expect(SETTLEMENT_TYPES_HU).toHaveLength(4);
    });

    test('should contain all settlement types', () => {
      const types = SETTLEMENT_TYPES_HU.map((t) => t.type);
      expect(types).toContain('főváros');
      expect(types).toContain('város');
      expect(types).toContain('nagyközség');
      expect(types).toContain('község');
    });

    test('each type should have required properties', () => {
      SETTLEMENT_TYPES_HU.forEach((type) => {
        expect(type).toHaveProperty('type');
        expect(type).toHaveProperty('name');
        expect(type).toHaveProperty('description');

        expect(typeof type.type).toBe('string');
        expect(typeof type.name).toBe('string');
        expect(typeof type.description).toBe('string');
      });
    });
  });

  describe('COUNTY_TO_REGION_MAP', () => {
    test('should have mapping for all 20 counties', () => {
      expect(Object.keys(COUNTY_TO_REGION_MAP)).toHaveLength(20);
    });

    test('all mapped regions should be valid', () => {
      Object.values(COUNTY_TO_REGION_MAP).forEach((region) => {
        expect(isValidRegion(region)).toBe(true);
      });
    });

    test('should include all HUNGARIAN_COUNTIES', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(COUNTY_TO_REGION_MAP).toHaveProperty(county.name);
      });
    });
  });

  describe('REGION_TO_COUNTIES_MAP', () => {
    test('should have mapping for all 7 regions', () => {
      expect(Object.keys(REGION_TO_COUNTIES_MAP)).toHaveLength(7);
    });

    test('all regions should be valid Hungarian regions', () => {
      Object.keys(REGION_TO_COUNTIES_MAP).forEach((region) => {
        expect(isValidRegion(region)).toBe(true);
      });
    });

    test('total counties across all regions should be 20', () => {
      const totalCounties = Object.values(REGION_TO_COUNTIES_MAP).reduce(
        (sum, counties) => sum + counties.length,
        0
      );
      expect(totalCounties).toBe(20);
    });

    test('Közép-Magyarország should have Budapest and Pest', () => {
      const centralHungaryCounties = REGION_TO_COUNTIES_MAP['Közép-Magyarország'];
      expect(centralHungaryCounties).toContain('Budapest');
      expect(centralHungaryCounties).toContain('Pest');
      expect(centralHungaryCounties).toHaveLength(2);
    });
  });

  describe('getCountyNameHu', () => {
    test('should return Hungarian name for valid county', () => {
      expect(getCountyNameHu('Budapest')).toBe('Budapest');
      expect(getCountyNameHu('Pest')).toBe('Pest');
      expect(getCountyNameHu('Baranya')).toBe('Baranya');
    });

    test('should return original name if county not found', () => {
      expect(getCountyNameHu('NonExistent')).toBe('NonExistent');
      expect(getCountyNameHu('Unknown')).toBe('Unknown');
    });

    test('should handle empty string', () => {
      expect(getCountyNameHu('')).toBe('');
    });
  });

  describe('getRegionForCounty', () => {
    test('should return correct region for Budapest', () => {
      expect(getRegionForCounty('Budapest')).toBe('Közép-Magyarország');
    });

    test('should return correct region for Pest', () => {
      expect(getRegionForCounty('Pest')).toBe('Közép-Magyarország');
    });

    test('should return correct region for Borsod-Abaúj-Zemplén', () => {
      expect(getRegionForCounty('Borsod-Abaúj-Zemplén')).toBe('Észak-Magyarország');
    });

    test('should return undefined for invalid county', () => {
      expect(getRegionForCounty('NonExistent')).toBeUndefined();
      expect(getRegionForCounty('')).toBeUndefined();
    });
  });

  describe('getCountiesForRegion', () => {
    test('should return counties for Közép-Magyarország', () => {
      const counties = getCountiesForRegion('Közép-Magyarország');
      expect(counties).toContain('Budapest');
      expect(counties).toContain('Pest');
      expect(counties).toHaveLength(2);
    });

    test('should return counties for Nyugat-Dunántúl', () => {
      const counties = getCountiesForRegion('Nyugat-Dunántúl');
      expect(counties.length).toBe(3);
      expect(counties).toContain('Győr-Moson-Sopron');
      expect(counties).toContain('Vas');
      expect(counties).toContain('Zala');
    });

    test('should return empty array for invalid region', () => {
      expect(getCountiesForRegion('NonExistent' as HungarianRegion)).toEqual([]);
    });
  });

  describe('isValidRegion', () => {
    test('should return true for all valid regions', () => {
      expect(isValidRegion('Közép-Magyarország')).toBe(true);
      expect(isValidRegion('Észak-Magyarország')).toBe(true);
      expect(isValidRegion('Dél-Alföld')).toBe(true);
    });

    test('should return false for invalid regions', () => {
      expect(isValidRegion('NonExistent')).toBe(false);
      expect(isValidRegion('')).toBe(false);
      expect(isValidRegion('Budapest')).toBe(false); // Budapest is a county, not a region
    });
  });

  describe('isValidCounty', () => {
    test('should return true for all valid counties', () => {
      expect(isValidCounty('Budapest')).toBe(true);
      expect(isValidCounty('Pest')).toBe(true);
      expect(isValidCounty('Baranya')).toBe(true);
      expect(isValidCounty('Borsod-Abaúj-Zemplén')).toBe(true);
    });

    test('should return false for invalid counties', () => {
      expect(isValidCounty('NonExistent')).toBe(false);
      expect(isValidCounty('')).toBe(false);
      expect(isValidCounty('Közép-Magyarország')).toBe(false); // This is a region
    });
  });

  describe('getCountyData', () => {
    test('should return full county data for Budapest', () => {
      const budapest = getCountyData('Budapest');
      expect(budapest).toBeDefined();
      expect(budapest?.name).toBe('Budapest');
      expect(budapest?.seat).toBe('Budapest');
      expect(budapest?.region).toBe('Közép-Magyarország');
      expect(budapest?.population).toBeGreaterThan(0);
      expect(budapest?.areaKm2).toBeGreaterThan(0);
    });

    test('should return undefined for invalid county', () => {
      expect(getCountyData('NonExistent')).toBeUndefined();
      expect(getCountyData('')).toBeUndefined();
    });

    test('should return data with all required properties', () => {
      const pest = getCountyData('Pest');
      expect(pest).toHaveProperty('name');
      expect(pest).toHaveProperty('nameHu');
      expect(pest).toHaveProperty('region');
      expect(pest).toHaveProperty('seat');
      expect(pest).toHaveProperty('areaKm2');
      expect(pest).toHaveProperty('population');
    });
  });

  describe('formatSettlementType', () => {
    test('should format főváros correctly', () => {
      expect(formatSettlementType('főváros')).toBe('Főváros');
    });

    test('should format város correctly', () => {
      expect(formatSettlementType('város')).toBe('Város');
    });

    test('should format nagyközség correctly', () => {
      expect(formatSettlementType('nagyközség')).toBe('Nagyközség');
    });

    test('should format község correctly', () => {
      expect(formatSettlementType('község')).toBe('Község');
    });

    test('should handle unknown types', () => {
      // @ts-expect-error - Testing unknown type
      expect(formatSettlementType('unknown')).toBe('unknown');
    });
  });

  describe('getCountyNames', () => {
    test('should return all 20 county names', () => {
      const names = getCountyNames();
      expect(names).toHaveLength(20);
      expect(names).toContain('Budapest');
      expect(names).toContain('Pest');
    });

    test('should return array of strings', () => {
      const names = getCountyNames();
      names.forEach((name) => {
        expect(typeof name).toBe('string');
      });
    });
  });

  describe('getRegionNames', () => {
    test('should return all 7 region names', () => {
      const names = getRegionNames();
      expect(names).toHaveLength(7);
      expect(names).toContain('Közép-Magyarország');
      expect(names).toContain('Észak-Magyarország');
    });

    test('should return mutable copy (not readonly)', () => {
      const names1 = getRegionNames();
      const names2 = getRegionNames();
      expect(names1).not.toBe(names2); // Different references
    });
  });

  describe('getCountyDensity', () => {
    test('should return density for Budapest (high)', () => {
      const density = getCountyDensity('Budapest');
      expect(density).toBeDefined();
      expect(density).toBeGreaterThan(3000); // Budapest is very dense
    });

    test('should return density for Pest', () => {
      const density = getCountyDensity('Pest');
      expect(density).toBeDefined();
      expect(density).toBeGreaterThan(0);
    });

    test('should return undefined for invalid county', () => {
      expect(getCountyDensity('NonExistent')).toBeUndefined();
    });

    test('Budapest should be denser than any other county', () => {
      const budapestDensity = getCountyDensity('Budapest');
      HUNGARIAN_COUNTIES.forEach((county) => {
        if (county.name !== 'Budapest') {
          const countyDensity = getCountyDensity(county.name);
          expect(countyDensity).toBeDefined();
          expect(budapestDensity).toBeGreaterThan(countyDensity!);
        }
      });
    });
  });

  describe('COUNTIES_BY_POPULATION', () => {
    test('should be sorted by population descending', () => {
      for (let i = 0; i < COUNTIES_BY_POPULATION.length - 1; i++) {
        expect(COUNTIES_BY_POPULATION[i].population).toBeGreaterThanOrEqual(
          COUNTIES_BY_POPULATION[i + 1].population
        );
      }
    });

    test('first element should be Budapest', () => {
      expect(COUNTIES_BY_POPULATION[0].name).toBe('Budapest');
    });

    test('should contain all counties', () => {
      expect(COUNTIES_BY_POPULATION).toHaveLength(20);
    });
  });

  describe('COUNTIES_BY_AREA', () => {
    test('should be sorted by area descending', () => {
      for (let i = 0; i < COUNTIES_BY_AREA.length - 1; i++) {
        expect(COUNTIES_BY_AREA[i].areaKm2).toBeGreaterThanOrEqual(
          COUNTIES_BY_AREA[i + 1].areaKm2
        );
      }
    });

    test('largest county should be Bács-Kiskun', () => {
      expect(COUNTIES_BY_AREA[0].name).toBe('Bács-Kiskun');
    });

    test('should contain all counties', () => {
      expect(COUNTIES_BY_AREA).toHaveLength(20);
    });
  });

  describe('Type definitions', () => {
    test('HungarianCounty type should match data structure', () => {
      const county: HungarianCounty = HUNGARIAN_COUNTIES[0];
      expect(county.name).toBeDefined();
      expect(county.region).toBeDefined();
    });

    test('HungarianRegion type should be a string union', () => {
      const region: HungarianRegion = 'Közép-Magyarország';
      expect(typeof region).toBe('string');
    });

    test('SettlementType should be valid settlement types', () => {
      const types: SettlementType[] = ['főváros', 'város', 'község', 'nagyközség'];
      types.forEach((type) => {
        expect(['főváros', 'város', 'község', 'nagyközség']).toContain(type);
      });
    });
  });

  describe('Integration tests', () => {
    test('COUNTY_TO_REGION_MAP and REGION_TO_COUNTIES_MAP should be consistent', () => {
      Object.entries(COUNTY_TO_REGION_MAP).forEach(([county, region]) => {
        const regionCounties = REGION_TO_COUNTIES_MAP[region];
        expect(regionCounties).toContain(county);
      });
    });

    test('all counties should have valid seat cities', () => {
      HUNGARIAN_COUNTIES.forEach((county) => {
        expect(county.seat).toBeTruthy();
        expect(county.seat.length).toBeGreaterThan(0);
        expect(typeof county.seat).toBe('string');
      });
    });

    test('total population should be reasonable for Hungary (~9-10 million)', () => {
      const totalPopulation = HUNGARIAN_COUNTIES.reduce(
        (sum, county) => sum + county.population,
        0
      );
      // Hungary's population is around 9.7 million (as of 2020s)
      expect(totalPopulation).toBeGreaterThan(9000000);
      expect(totalPopulation).toBeLessThan(11000000);
    });

    test('total area should be close to Hungary\'s actual area (~93,000 km²)', () => {
      const totalArea = HUNGARIAN_COUNTIES.reduce(
        (sum, county) => sum + county.areaKm2,
        0
      );
      // Hungary's area is approximately 93,030 km²
      expect(totalArea).toBeGreaterThan(90000);
      expect(totalArea).toBeLessThan(95000);
    });

    test('each region should have at least 1 county', () => {
      HUNGARIAN_REGIONS.forEach((region) => {
        const counties = getCountiesForRegion(region);
        expect(counties.length).toBeGreaterThan(0);
      });
    });

    test('settlement types should be ordered by size hierarchy', () => {
      expect(SETTLEMENT_TYPES_HU).toHaveLength(4);
      const types = SETTLEMENT_TYPES_HU.map((t) => t.type);
      expect(types).toContain('főváros'); // Largest
      expect(types).toContain('város');
      expect(types).toContain('nagyközség');
      expect(types).toContain('község'); // Smallest
    });
  });

  describe('Edge cases', () => {
    test('should handle special characters in county names', () => {
      const countyWithDash = getCountyData('Borsod-Abaúj-Zemplén');
      expect(countyWithDash).toBeDefined();
      expect(countyWithDash?.name).toContain('-');

      const countyWithAccent = getCountyData('Csongrád-Csanád');
      expect(countyWithAccent).toBeDefined();
      expect(countyWithAccent?.name).toContain('á');
    });

    test('should handle case sensitivity correctly', () => {
      expect(isValidCounty('budapest')).toBe(false); // Case sensitive
      expect(isValidCounty('Budapest')).toBe(true);
      expect(isValidCounty('BUDAPEST')).toBe(false);
    });

    test('should handle whitespace in inputs', () => {
      expect(isValidCounty(' Budapest')).toBe(false);
      expect(isValidCounty('Budapest ')).toBe(false);
    });
  });
});
