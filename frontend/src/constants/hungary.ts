/**
 * Hungary Constants - Geographic data and administrative divisions
 *
 * Hungary administrative structure:
 * - 7 statistical regions (statisztikai régiók)
 * - 20 counties (19 megye + Budapest)
 * - ~3150 settlements (városok, községek, nagyközségek)
 *
 * Reference: https://en.wikipedia.org/wiki/Counties_of_Hungary
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

/**
 * Hungarian county (megye)
 */
export interface HungarianCounty {
  name: string;
  nameHu: string;
  region: HungarianRegion;
  seat: string;
  areaKm2: number;
  population: number;
}

/**
 * Hungarian statistical region (statisztikai régió)
 */
export type HungarianRegion =
  | 'Közép-Magyarország'
  | 'Észak-Magyarország'
  | 'Észak-Alföld'
  | 'Dél-Alföld'
  | 'Dél-Dunántúl'
  | 'Nyugat-Dunántúl'
  | 'Közép-Dunántúl';

/**
 * Settlement type (településtípus)
 */
export type SettlementType = 'város' | 'község' | 'főváros' | 'nagyközség';

/**
 * Hungarian settlement (település)
 */
export interface HungarianSettlement {
  name: string;
  county: string;
  settlement_type: SettlementType;
  coordinates?: {
    lat: number;
    lon: number;
  };
  population?: number;
  region_priority?: number;
}

/**
 * Weather station (meteorológiai állomás)
 */
export interface HungarianWeatherStation {
  id: string;
  name: string;
  county: string;
  settlement_type: SettlementType;
  coordinates?: {
    lat: number;
    lon: number;
  };
  population?: number;
  region_priority?: number;
}

/**
 * API response for counties
 */
export interface CountiesResponse {
  count: number;
  counties: string[];
}

/**
 * API response for regions
 */
export interface RegionsResponse {
  count: number;
  regions: HungarianRegion[];
}

/**
 * API response for settlements
 */
export interface SettlementsResponse {
  count: number;
  filter?: {
    county?: string;
    settlement_type?: SettlementType;
  };
  settlements: HungarianSettlement[];
}

/**
 * API response for weather stations
 */
export interface StationsResponse {
  count: number;
  filter?: {
    county?: string;
  };
  stations: HungarianWeatherStation[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Hungarian statistical regions (7 db)
 */
export const HUNGARIAN_REGIONS: readonly HungarianRegion[] = [
  'Közép-Magyarország',
  'Észak-Magyarország',
  'Észak-Alföld',
  'Dél-Alföld',
  'Dél-Dunántúl',
  'Nyugat-Dunántúl',
  'Közép-Dunántúl'
] as const;

/**
 * Hungarian counties (20: Budapest + 19 megye)
 * Ordered alphabetically with Budapest first
 */
export const HUNGARIAN_COUNTIES: readonly HungarianCounty[] = [
  {
    name: 'Budapest',
    nameHu: 'Budapest',
    region: 'Közép-Magyarország',
    seat: 'Budapest',
    areaKm2: 525,
    population: 1752000
  },
  {
    name: 'Bács-Kiskun',
    nameHu: 'Bács-Kiskun',
    region: 'Dél-Alföld',
    seat: 'Kecskemét',
    areaKm2: 8445,
    population: 509000
  },
  {
    name: 'Baranya',
    nameHu: 'Baranya',
    region: 'Dél-Dunántúl',
    seat: 'Pécs',
    areaKm2: 4430,
    population: 376000
  },
  {
    name: 'Békés',
    nameHu: 'Békés',
    region: 'Dél-Alföld',
    seat: 'Békéscsaba',
    areaKm2: 5630,
    population: 350000
  },
  {
    name: 'Borsod-Abaúj-Zemplén',
    nameHu: 'Borsod-Abaúj-Zemplén',
    region: 'Észak-Magyarország',
    seat: 'Miskolc',
    areaKm2: 7247,
    population: 668000
  },
  {
    name: 'Csongrád-Csanád',
    nameHu: 'Csongrád-Csanád',
    region: 'Dél-Alföld',
    seat: 'Szeged',
    areaKm2: 4263,
    population: 406000
  },
  {
    name: 'Fejér',
    nameHu: 'Fejér',
    region: 'Közép-Dunántúl',
    seat: 'Székesfehérvár',
    areaKm2: 4359,
    population: 421000
  },
  {
    name: 'Győr-Moson-Sopron',
    nameHu: 'Győr-Moson-Sopron',
    region: 'Nyugat-Dunántúl',
    seat: 'Győr',
    areaKm2: 4089,
    population: 465000
  },
  {
    name: 'Hajdú-Bihar',
    nameHu: 'Hajdú-Bihar',
    region: 'Észak-Alföld',
    seat: 'Debrecen',
    areaKm2: 6211,
    population: 527000
  },
  {
    name: 'Heves',
    nameHu: 'Heves',
    region: 'Észak-Magyarország',
    seat: 'Eger',
    areaKm2: 3637,
    population: 295000
  },
  {
    name: 'Jász-Nagykun-Szolnok',
    nameHu: 'Jász-Nagykun-Szolnok',
    region: 'Észak-Alföld',
    seat: 'Szolnok',
    areaKm2: 5582,
    population: 374000
  },
  {
    name: 'Komárom-Esztergom',
    nameHu: 'Komárom-Esztergom',
    region: 'Közép-Dunántúl',
    seat: 'Tatabánya',
    areaKm2: 2265,
    population: 299000
  },
  {
    name: 'Nógrád',
    nameHu: 'Nógrád',
    region: 'Észak-Magyarország',
    seat: 'Salgótarján',
    areaKm2: 2544,
    population: 194000
  },
  {
    name: 'Pest',
    nameHu: 'Pest',
    region: 'Közép-Magyarország',
    seat: 'Budapest',
    areaKm2: 6393,
    population: 1290000
  },
  {
    name: 'Somogy',
    nameHu: 'Somogy',
    region: 'Dél-Dunántúl',
    seat: 'Kaposvár',
    areaKm2: 6036,
    population: 310000
  },
  {
    name: 'Szabolcs-Szatmár-Bereg',
    nameHu: 'Szabolcs-Szatmár-Bereg',
    region: 'Észak-Alföld',
    seat: 'Nyíregyháza',
    areaKm2: 5936,
    population: 549000
  },
  {
    name: 'Tolna',
    nameHu: 'Tolna',
    region: 'Dél-Dunántúl',
    seat: 'Szekszárd',
    areaKm2: 3703,
    population: 213000
  },
  {
    name: 'Vas',
    nameHu: 'Vas',
    region: 'Nyugat-Dunántúl',
    seat: 'Szombathely',
    areaKm2: 3357,
    population: 244000
  },
  {
    name: 'Veszprém',
    nameHu: 'Veszprém',
    region: 'Közép-Dunántúl',
    seat: 'Veszprém',
    areaKm2: 4613,
    population: 342000
  },
  {
    name: 'Zala',
    nameHu: 'Zala',
    region: 'Nyugat-Dunántúl',
    seat: 'Zalaegerszeg',
    areaKm2: 3844,
    population: 268000
  }
] as const;

/**
 * Settlement types in Hungarian
 */
export const SETTLEMENT_TYPES_HU: readonly { type: SettlementType; name: string; description: string }[] = [
  { type: 'főváros', name: 'Főváros', description: 'Capital city' },
  { type: 'város', name: 'Város', description: 'City/town' },
  { type: 'nagyközség', name: 'Nagyközség', description: 'Large village' },
  { type: 'község', name: 'Község', description: 'Village' }
] as const;

/**
 * County to region mapping
 */
export const COUNTY_TO_REGION_MAP: Readonly<Record<string, HungarianRegion>> = {
  'Budapest': 'Közép-Magyarország',
  'Pest': 'Közép-Magyarország',
  'Fejér': 'Közép-Dunántúl',
  'Komárom-Esztergom': 'Közép-Dunántúl',
  'Veszprém': 'Közép-Dunántúl',
  'Győr-Moson-Sopron': 'Nyugat-Dunántúl',
  'Vas': 'Nyugat-Dunántúl',
  'Zala': 'Nyugat-Dunántúl',
  'Borsod-Abaúj-Zemplén': 'Észak-Magyarország',
  'Heves': 'Észak-Magyarország',
  'Nógrád': 'Észak-Magyarország',
  'Hajdú-Bihar': 'Észak-Alföld',
  'Jász-Nagykun-Szolnok': 'Észak-Alföld',
  'Szabolcs-Szatmár-Bereg': 'Észak-Alföld',
  'Békés': 'Dél-Alföld',
  'Csongrád-Csanád': 'Dél-Alföld',
  'Bács-Kiskun': 'Dél-Alföld',
  'Baranya': 'Dél-Dunántúl',
  'Somogy': 'Dél-Dunántúl',
  'Tolna': 'Dél-Dunántúl'
} as const;

/**
 * Region to counties mapping
 */
export const REGION_TO_COUNTIES_MAP: Readonly<Record<HungarianRegion, string[]>> = {
  'Közép-Magyarország': ['Budapest', 'Pest'],
  'Észak-Magyarország': ['Borsod-Abaúj-Zemplén', 'Heves', 'Nógrád'],
  'Észak-Alföld': ['Hajdú-Bihar', 'Jász-Nagykun-Szolnok', 'Szabolcs-Szatmár-Bereg'],
  'Dél-Alföld': ['Békés', 'Csongrád-Csanád', 'Bács-Kiskun'],
  'Dél-Dunántúl': ['Baranya', 'Somogy', 'Tolna'],
  'Nyugat-Dunántúl': ['Győr-Moson-Sopron', 'Vas', 'Zala'],
  'Közép-Dunántúl': ['Fejér', 'Komárom-Esztergom', 'Veszprém']
} as const;

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get county name in Hungarian
 */
export function getCountyNameHu(county: string): string {
  const countyData = HUNGARIAN_COUNTIES.find(c => c.name === county);
  return countyData?.nameHu ?? county;
}

/**
 * Get region for a county
 */
export function getRegionForCounty(county: string): HungarianRegion | undefined {
  return COUNTY_TO_REGION_MAP[county];
}

/**
 * Get counties for a region
 */
export function getCountiesForRegion(region: HungarianRegion): string[] {
  return REGION_TO_COUNTIES_MAP[region] ?? [];
}

/**
 * Check if a string is a valid Hungarian region
 */
export function isValidRegion(region: string): region is HungarianRegion {
  return HUNGARIAN_REGIONS.includes(region as HungarianRegion);
}

/**
 * Check if a string is a valid Hungarian county
 */
export function isValidCounty(county: string): boolean {
  return HUNGARIAN_COUNTIES.some(c => c.name === county);
}

/**
 * Get county data by name
 */
export function getCountyData(county: string): HungarianCounty | undefined {
  return HUNGARIAN_COUNTIES.find(c => c.name === county);
}

/**
 * Format settlement type in Hungarian
 */
export function formatSettlementType(type: SettlementType): string {
  const typeData = SETTLEMENT_TYPES_HU.find(t => t.type === type);
  return typeData?.name ?? type;
}

/**
 * Get all county names as string array
 */
export function getCountyNames(): string[] {
  return HUNGARIAN_COUNTIES.map(c => c.name);
}

/**
 * Get all region names as string array
 */
export function getRegionNames(): HungarianRegion[] {
  return [...HUNGARIAN_REGIONS];
}

/**
 * Calculate county population density (people/km²)
 */
export function getCountyDensity(county: string): number | undefined {
  const countyData = getCountyData(county);
  if (!countyData) return undefined;
  return Math.round(countyData.population / countyData.areaKm2);
}

/**
 * Counties ordered by population (descending)
 */
export const COUNTIES_BY_POPULATION = [...HUNGARIAN_COUNTIES].sort((a, b) => b.population - a.population);

/**
 * Counties ordered by area (descending)
 */
export const COUNTIES_BY_AREA = [...HUNGARIAN_COUNTIES].sort((a, b) => b.areaKm2 - a.areaKm2);
