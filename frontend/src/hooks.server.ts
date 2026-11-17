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
	const canonical = new URL(input.event.url);
	canonical.hostname = canonical.hostname.replace(/^www\./, '');
	canonical.pathname = canonical.pathname.replace(/\/+$/, '') || '/';
	if (canonical.href !== input.event.url.href) {
		return new Response(null, { status: 308, headers: { location: canonical.href } });
	}

	const response = await handleParaglide(input);

	if (input.event.route.id?.includes('[token]')) {
		response.headers.set('X-Robots-Tag', 'noindex, nofollow');
		response.headers.set('Referrer-Policy', 'no-referrer');
	}

	return response;
};
