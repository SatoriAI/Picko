import type { RequestHandler } from './$types';

// A route rather than a static file because the Sitemap line must be an absolute URL on the host being served.
// Secret-link pages stay crawlable on purpose: they answer with X-Robots-Tag noindex, which a crawler only sees if it
// may fetch them.
export const GET: RequestHandler = ({ url }) =>
	new Response(
		`User-agent: *\nDisallow:\n\nSitemap: ${new URL('/sitemap.xml', url.origin).href}\n`,
		{
			headers: {
				'Content-Type': 'text/plain; charset=utf-8',
				'Cache-Control': 'public, max-age=3600'
			}
		}
	);
