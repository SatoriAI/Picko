import { locales, localizeUrl, type Locale } from '$lib/paraglide/runtime';

// Only the homepage is meant to be found by search: every other page is reached through a secret link.

export const homeUrl = (origin: string): string => new URL('/', origin).href;

export const localizedHome = (origin: string, locale: Locale): string =>
	localizeUrl(new URL('/', origin), { locale }).href;

/** The homepage in every language, plus `/` as the x-default that redirects to the visitor's language. */
export const homeAlternates = (origin: string): Array<{ hreflang: string; href: string }> => [
	...locales.map((locale) => ({ hreflang: locale, href: localizedHome(origin, locale) })),
	{ hreflang: 'x-default', href: homeUrl(origin) }
];
