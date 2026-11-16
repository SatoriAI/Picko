import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { paraglideMiddleware } from '$lib/paraglide/server';

const handleParaglide: Handle = ({ event, resolve }) =>
	paraglideMiddleware(event.request, ({ request, locale }) => {
		event.request = request;

		return resolve(event, {
			transformPageChunk: ({ html }) => html.replace('%paraglide.lang%', locale)
		});
	});

// A secret link is the only access control, so a page reached by one must not be indexed, and its address must not
// leave in the Referer header when someone follows an outbound link from it.
export const handleTokenRoutes: Handle = async ({ event, resolve }) => {
	const response = await resolve(event);

	if (event.route.id?.includes('[token]')) {
		response.headers.set('X-Robots-Tag', 'noindex, nofollow');
		response.headers.set('Referrer-Policy', 'no-referrer');
	}

	return response;
};

export const handle: Handle = sequence(handleTokenRoutes, handleParaglide);
