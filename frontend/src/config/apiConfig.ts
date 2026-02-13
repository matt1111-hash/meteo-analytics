/**
 * API Configuration
 *
 * Centralized API configuration with environment variable support.
 *
 * Usage:
 * - Development: Create .env file in frontend/ with REACT_APP_API_BASE_URL=http://localhost:8003
 * - Production: Set REACT_APP_API_BASE_URL environment variable to your production API URL
 *
 * Security Note:
 * - If API_KEY is enabled on backend, set REACT_APP_API_KEY environment variable
 * - Never commit .env files with real API keys to version control
 */

// API Base URL - defaults to localhost:8003 for development
export const API_BASE_URL: string =
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8003';

// API Key for authentication (optional)
// Set REACT_APP_API_KEY in .env if backend has API_KEY enabled
export const API_KEY: string | undefined = process.env.REACT_APP_API_KEY;

// Whether API key is configured
export const API_KEY_ENABLED: boolean = API_KEY !== undefined && API_KEY !== '';

/**
 * Get headers for API requests including auth if configured
 */
export const getApiHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (API_KEY_ENABLED) {
    headers['X-API-Key'] = API_KEY!;
  }

  return headers;
};

/**
 * API configuration object for convenience
 */
export const apiConfig = {
  baseUrl: API_BASE_URL,
  apiKey: API_KEY,
  apiKeyEnabled: API_KEY_ENABLED,
  headers: getApiHeaders,
};
