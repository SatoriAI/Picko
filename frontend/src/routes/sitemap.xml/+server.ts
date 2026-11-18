import type { RequestHandler } from './$types';
import { locales } from '$lib/paraglide/runtime';
import { INDEXED_ROUTES, localizedPage, pageAlternates } from '$lib/seo';

// Built per request rather than prerendered, so the hosts are whatever the site is served from.
export const GET: RequestHandler = ({ url }) => {
	const entries = INDEXED_ROUTES.flatMap((route) => {
		const alternates = pageAlternates(url.origin, route)
			.map(
				({ hreflang, href }) =>
					`\t\t<xhtml:link rel="alternate" hreflang="${hreflang}" href="${href}"/>`
			)
			.join('\n');
		return locales.map(
			(locale) =>
				`\t<url>\n\t\t<loc>${localizedPage(url.origin, route, locale)}</loc>\n${alternates}\n\t</url>`
		);
	}).join('\n');

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${entries}
</urlset>
`;

	return new Response(xml, {
		headers: {
			'Content-Type': 'application/xml; charset=utf-8',
			'Cache-Control': 'public, max-age=3600'
		}
	});
};
