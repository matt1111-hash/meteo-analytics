/**
 * Production-safe logger.
 * All console output is stripped in production builds via dead-code elimination.
 */

const isDev = import.meta.env.DEV;

export const logger = {
  debug: (...args: unknown[]): void => {
    if (isDev) console.log('[DEBUG]', ...args);
  },
  info: (...args: unknown[]): void => {
    if (isDev) console.info('[INFO]', ...args);
  },
  warn: (...args: unknown[]): void => {
    if (isDev) console.warn('[WARN]', ...args);
  },
  error: (...args: unknown[]): void => {
    // Errors are always logged but without sensitive response data
    console.error('[ERROR]', ...args);
  },
};
