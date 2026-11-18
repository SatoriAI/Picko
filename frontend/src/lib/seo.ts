import { baseLocale, locales, localizeUrl, type Locale } from '$lib/paraglide/runtime';
import { GUIDE_IDS, guideRoute } from '$lib/guides/paths';

// Only the homepage and the guides are meant to be found by search: every other page is reached through a secret link.

/** The app routes that search engines should index, each served at one address per language. */
export const INDEXED_ROUTES: string[] = ['/', ...GUIDE_IDS.map(guideRoute)];

/** The public address of an app route in one language, e.g. `/guides/work` in Polish → `…/pl/mikolajki-w-pracy`. */
export const localizedPage = (origin: string, route: string, locale: Locale): string =>
	localizeUrl(new URL(route, origin), { locale }).href;

/**
 * A page in every language, plus the base-language version as x-default. Not `/` for the homepage: it redirects only
 * browsers (Paraglide checks Sec-Fetch-Dest), so a crawler gets `/` as a page whose canonical is a language page, and
 * an x-default that canonicalises elsewhere is a contradiction search engines may ignore.
 */
export const pageAlternates = (
	origin: string,
	route: string
): Array<{ hreflang: string; href: string }> => [
	...locales.map((locale) => ({ hreflang: locale, href: localizedPage(origin, route, locale) })),
	{ hreflang: 'x-default', href: localizedPage(origin, route, baseLocale) }
];
