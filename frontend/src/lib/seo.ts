import { baseLocale, locales, localizeUrl, type Locale } from '$lib/paraglide/runtime';

// Only the homepage is meant to be found by search: every other page is reached through a secret link.

export const localizedHome = (origin: string, locale: Locale): string =>
	localizeUrl(new URL('/', origin), { locale }).href;

/**
 * The homepage in every language, plus the base-language page as x-default. Not `/`: it redirects only browsers
 * (Paraglide checks Sec-Fetch-Dest), so a crawler gets `/` as a page whose canonical is a language page, and an
 * x-default that canonicalises elsewhere is a contradiction search engines may ignore.
 */
export const homeAlternates = (origin: string): Array<{ hreflang: string; href: string }> => [
	...locales.map((locale) => ({ hreflang: locale, href: localizedHome(origin, locale) })),
	{ hreflang: 'x-default', href: localizedHome(origin, baseLocale) }
];
