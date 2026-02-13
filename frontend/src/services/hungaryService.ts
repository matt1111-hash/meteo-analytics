/**
 * Hungary Service - Hungarian regions, counties, and settlements
 */
import axios from 'axios';

import { API_BASE_URL, getApiHeaders } from '../config/apiConfig';

// =============================================================================
// TYPES
// =============================================================================

export interface HungarianCounty {
  name: string;
}

export interface HungarianRegion {
  name: string;
}

export interface HungarianSettlement {
  name: string;
  county: string | null;
  settlement_type: string | null;
  coordinates: {
    lat: number;
    lon: number;
  } | null;
  population: number | null;
  region_priority: number | null;
}

export interface HungarianWeatherStation {
  id: string;
  name: string;
  county: string | null;
  coordinates: {
    lat: number;
    lon: number;
  } | null;
  population: number | null;
  data_quality_score: number | null;
}

export interface CountiesResponse {
  count: number;
  counties: string[];
}

export interface RegionsResponse {
  count: number;
  regions: string[];
}

export interface SettlementsResponse {
  count: number;
  filter: {
    county: string | null;
    settlement_type: string | null;
  };
  settlements: HungarianSettlement[];
}

export interface StationsResponse {
  count: number;
  filter: {
    county: string | null;
  };
  stations: HungarianWeatherStation[];
}

// =============================================================================
// API FUNCTIONS
// =============================================================================

/**
 * Get list of Hungarian counties (19 counties + Budapest)
 */
export const getHungarianCounties = async (): Promise<CountiesResponse> => {
  const response = await axios.get<CountiesResponse>(
    `${API_BASE_URL}/api/hungary/counties`
  );
  return response.data;
};

/**
 * Get list of Hungarian statistical regions (7 regions)
 */
export const getHungarianRegions = async (): Promise<RegionsResponse> => {
  const response = await axios.get<RegionsResponse>(
    `${API_BASE_URL}/api/hungary/regions`
  );
  return response.data;
};

/**
 * Get Hungarian settlements with optional filtering
 *
 * @param options - Filter options
 * @param options.county - Filter by county (e.g., "Pest", "Bács-Kiskun")
 * @param options.settlementType - Filter by type ("város", "község", "nagyközség")
 * @param options.limit - Maximum results (1-500, default 50)
 */
export const getHungarianSettlements = async (options?: {
  county?: string;
  settlementType?: string;
  limit?: number;
}): Promise<SettlementsResponse> => {
  const params = new URLSearchParams();
  if (options?.county) params.append('county', options.county);
  if (options?.settlementType) params.append('settlement_type', options.settlementType);
  if (options?.limit) params.append('limit', options.limit.toString());

  const response = await axios.get<SettlementsResponse>(
    `${API_BASE_URL}/api/hungary/settlements?${params.toString()}`
  );
  return response.data;
};

/**
 * Get Hungarian weather stations (Meteostat)
 *
 * @param options - Filter options
 * @param options.county - Filter by county
 * @param options.limit - Maximum results (1-500, default 100)
 */
export const getHungarianWeatherStations = async (options?: {
  county?: string;
  limit?: number;
}): Promise<StationsResponse> => {
  const params = new URLSearchParams();
  if (options?.county) params.append('county', options.county);
  if (options?.limit) params.append('limit', options.limit.toString());

  const response = await axios.get<StationsResponse>(
    `${API_BASE_URL}/api/hungary/stations?${params.toString()}`
  );
  return response.data;
};

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * Hungarian statistical regions (statisztikai régiók)
 */
export const HUNGARIAN_REGIONS = [
  'Közép-Magyarország',
  'Észak-Magyarország',
  'Észak-Alföld',
  'Dél-Alföld',
  'Dél-Dunántúl',
  'Nyugat-Dunántúl',
  'Közép-Dunántúl',
] as const;

/**
 * Hungarian counties (megyék) - 19 counties + Budapest
 */
export const HUNGARIAN_COUNTIES = [
  'Budapest',
  'Bács-Kiskun',
  'Baranya',
  'Békés',
  'Borsod-Abaúj-Zemplén',
  'Csongrád-Csanád',
  'Fejér',
  'Győr-Moson-Sopron',
  'Hajdú-Bihar',
  'Heves',
  'Jász-Nagykun-Szolnok',
  'Komárom-Esztergom',
  'Nógrád',
  'Pest',
  'Somogy',
  'Szabolcs-Szatmár-Bereg',
  'Tolna',
  'Vas',
  'Veszprém',
  'Zala',
] as const;

/**
 * Hungarian settlement types
 */
export const SETTLEMENT_TYPES = [
  'város',          // city
  'nagyközség',     // large village
  'község',         // village
  'megyei jogú város', // city with county rights
] as const;
