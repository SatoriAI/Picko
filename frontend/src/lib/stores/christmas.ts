import { PUBLIC_CHRISTMAS_THEME } from '$env/static/public';

/**
 * Christmas theme toggle.
 * Controlled via PUBLIC_CHRISTMAS_THEME environment variable.
 * Set to "true" to enable festive decorations.
 */
export const CHRISTMAS_THEME = PUBLIC_CHRISTMAS_THEME === 'true';
