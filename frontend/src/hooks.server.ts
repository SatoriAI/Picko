import type { Handle } from '@sveltejs/kit';
import { paraglideMiddleware } from '$lib/paraglide/server';

const handleParaglide: Handle = ({ event, resolve }) =>
	paraglideMiddleware(event.request, ({ request, locale }) => {
		event.request = request;

		return resolve(event, {
			transformPageChunk: ({ html }) => html.replace('%paraglide.lang%', locale)
		});
	});

// A secret link is the only access control, so a page reached by one must not be indexed, and its address must not
// leave in the Referer header when someone follows an outbound link from it. This wraps Paraglide directly rather
// than going through sequence(), which needs SvelteKit's request context and so cannot be called from a test.
export const handle: Handle = async (input) => {
	// One address per page, so search engines don't split it into duplicates. `www.picko.world` served the whole site
	// under its own canonicals. `/en` and `/pl` exist only as Paraglide URL patterns, which don't match a trailing
	// slash, and no route matches `/pl/`, so SvelteKit's own trailing-slash redirect never runs for them and they would
	// answer 404. Both are fixed in one redirect, so a URL with both problems isn't sent through a chain.
	// Only page loads are redirected: an API call or data request from a page already open on www would turn into a
	// cross-origin request (or lose its `__data.json` suffix, which event.url omits), so those are served where they are.
	const { event } = input;
	const isPageLoad =
		(event.request.method === 'GET' || event.request.method === 'HEAD') && !event.isDataRequest;
	const canonical = new URL(event.url);
	canonical.hostname = canonical.hostname.replace(/^www\./, '');
	canonical.pathname = canonical.pathname.replace(/\/+$/, '') || '/';
	if (isPageLoad && canonical.href !== event.url.href) {
		// Relative when only the path changes, so that redirect never depends on the proxy reporting the right scheme.
		const location =
			canonical.origin === event.url.origin
				? canonical.pathname + canonical.search
				: canonical.href;
		return new Response(null, { status: 308, headers: { location } });
	}

	const response = await handleParaglide(input);

	if (input.event.route.id?.includes('[token]')) {
		response.headers.set('X-Robots-Tag', 'noindex, nofollow');
		response.headers.set('Referrer-Policy', 'no-referrer');
	}

	return response;
};
