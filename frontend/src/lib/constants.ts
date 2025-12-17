/**
 * Application-wide constants.
 */

/** Default currency used when none is specified */
export const DEFAULT_CURRENCY = 'PLN';

/** Supported currencies */
export const CURRENCIES = ['PLN', 'USD', 'EUR'] as const;

export type Currency = (typeof CURRENCIES)[number];
