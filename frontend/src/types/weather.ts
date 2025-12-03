// Weather API TypeScript Types
// Maps to backend: src/api/dto/weather_request.py + src/data/models.py

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface DateRange {
  date?: string;        // Single date: "2025-11-22"
  start?: string;       // Range start: "2025-11-01"
  end?: string;         // Range end: "2025-11-22"
}

export interface WeatherAnalysisRequest {
  cities: string[];
  date_range: DateRange;
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface AnalyticsQuestion {
  question_text: string;
  question_type: string;
  region_scope: string;
  metric: string;
  region_value: string | null;
  date_filter: string | null;
  ascending_order: boolean;
  max_cities: number;
  min_population: number | null;
  include_capitals_only: boolean;
  exclude_islands: boolean;
  climate_zones: string[] | null;
  created_at: string;
  created_by: string | null;
  tags: string[];
}

export interface CityWeatherResult {
  city_name: string;
  country: string;
  country_code: string;
  latitude: number;
  longitude: number;
  value: number;
  metric: string;
  date: string;
  rank: number | null;
  additional_data: Record<string, unknown>;
  data_source: string;
  quality_score: number;
  confidence: number;
  population: number | null;
  elevation: number | null;
  timezone: string | null;
  admin_name: string | null;
}

export interface WeatherAnalysisResponse {
  question: AnalyticsQuestion;
  city_results: CityWeatherResult[];
  execution_time: number;
  total_cities_found: number;
  data_sources_used: string[];
  statistics: Record<string, number>;
  provider_statistics: Record<string, unknown>;
  average_quality_score: number;
  average_confidence: number;
  created_at: string;
}

// ============================================================================
// METADATA TYPES
// ============================================================================

export interface MetricInfo {
  name: string;
  unit: string;
  description: string;
}

export interface MetricsResponse {
  metrics: Record<string, MetricInfo>;
  total_count: number;
  enum_values: string[];
}

// ============================================================================
// UI FORM DATA
// ============================================================================

// ============================================================================
// DETAILED VIEW RESPONSE TYPES
// ============================================================================

export interface DetailedData {
  temperature_data: CityWeatherResult[];
  wind_data: CityWeatherResult[];
  wind_gusts_data: CityWeatherResult[];
  precipitation_data: CityWeatherResult[];
}

// ============================================================================
// UI FORM DATA
// ============================================================================

export interface FormData {
  cities: string;        // Comma-separated city names
  dateType: 'single' | 'range';
  singleDate: string;
  startDate: string;
  endDate: string;
}
