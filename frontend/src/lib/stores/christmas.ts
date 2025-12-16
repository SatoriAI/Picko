import { env } from '$env/dynamic/public';

/**
 * Christmas theme toggle.
 * Controlled via PUBLIC_CHRISTMAS_THEME environment variable.
 * Set to "true" to enable festive decorations.
 */
export const CHRISTMAS_THEME = env.PUBLIC_CHRISTMAS_THEME === 'true';
