/**
 * API Configuration
 *
 * Centralized API configuration with environment variable support.
 *
 * Security:
 * - No API keys are stored client-side.
 * - If backend authentication is required, it must be handled via
 *   server-side session/proxy, not via browser-visible env vars.
 */

// API Base URL - defaults to localhost:8003 for development
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';

/**
 * Get headers for API requests.
 * Auth headers are NOT included — backend must use cookie/session auth
 * or be accessible without client-side secrets (e.g. via Vite proxy).
 */
export const getApiHeaders = (): Record<string, string> => ({
  'Content-Type': 'application/json',
});

/**
 * API configuration object for convenience
 */
export const apiConfig = {
  baseUrl: API_BASE_URL,
  headers: getApiHeaders,
};
