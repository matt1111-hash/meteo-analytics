/**
 * Centralized API client with retry logic and connection status tracking.
 *
 * All API calls should use this client instead of raw axios.
 * Provides:
 * - Automatic retry with exponential backoff for network errors
 * - Single retry for 5xx server errors
 * - Connection status tracking (backend up/down)
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

import { API_BASE_URL } from '../config/apiConfig';

// ---------------------------------------------------------------------------
// Connection status event system
// ---------------------------------------------------------------------------

type ConnectionListener = (connected: boolean) => void;

const listeners: Set<ConnectionListener> = new Set();
let connected = true;

/** Subscribe to backend connection changes. Returns unsubscribe fn. */
export const onConnectionChange = (fn: ConnectionListener): (() => void) => {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
};

/** Check if the backend was reachable on the last completed request. */
export const isBackendConnected = (): boolean => connected;

const setConnected = (value: boolean): void => {
  if (connected !== value) {
    connected = value;
    listeners.forEach((fn) => fn(value));
  }
};

// ---------------------------------------------------------------------------
// Retry helpers
// ---------------------------------------------------------------------------

const MAX_NETWORK_RETRIES = 3;
const INITIAL_DELAY_MS = 1000;
const BACKOFF_FACTOR = 2;
const MAX_5XX_RETRIES = 1;

/** Network-level codes that mean "backend is not running". */
const NETWORK_CODES = new Set(['ECONNREFUSED', 'ERR_NETWORK', 'ECONNRESET', 'ETIMEDOUT']);

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retryCount?: number;
}

function isNetworkError(err: AxiosError): boolean {
  return !err.response && !!err.code && NETWORK_CODES.has(err.code);
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
});

// --- Response interceptor: retry + connection status -----------------------

apiClient.interceptors.response.use(
  (response) => {
    setConnected(true);
    return response;
  },
  async (error: AxiosError) => {
    const cfg = error.config as RetryableConfig | undefined;
    if (!cfg) {
      return Promise.reject(error);
    }

    // --- Network error (backend unreachable) --------------------------------
    if (isNetworkError(error)) {
      setConnected(false);

      const retryCount = cfg._retryCount ?? 0;
      if (retryCount < MAX_NETWORK_RETRIES) {
        cfg._retryCount = retryCount + 1;
        const wait = INITIAL_DELAY_MS * BACKOFF_FACTOR ** retryCount;
        await delay(wait);
        return apiClient(cfg);
      }

      // All retries exhausted — enrich the error message
      const enhanced = new AxiosError(
        'Backend server is not reachable. Start it with: ' +
          'python -m uvicorn src.api.main:app --port 8003',
        error.code,
        error.config,
        error.request,
        error.response,
      );
      return Promise.reject(enhanced);
    }

    // --- Server responded (4xx / 5xx) → backend IS running ------------------
    setConnected(true);

    // Retry 5xx once
    if (error.response && error.response.status >= 500) {
      const retryCount = cfg._retryCount ?? 0;
      if (retryCount < MAX_5XX_RETRIES) {
        cfg._retryCount = retryCount + 1;
        await delay(1000);
        return apiClient(cfg);
      }
    }

    return Promise.reject(error);
  },
);

export default apiClient;
