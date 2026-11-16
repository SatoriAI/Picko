import { describe, expect, it } from 'vitest';
import type { RequestEvent } from '@sveltejs/kit';
import { handleTokenRoutes } from './hooks.server';

async function headersFor(routeId: string | null): Promise<Headers> {
	const event = { route: { id: routeId } } as RequestEvent;
	const response = await handleTokenRoutes({ event, resolve: async () => new Response('ok') });
	return response.headers;
}

describe('handleTokenRoutes', () => {
	it.each([
		'/event/[token]',
		'/register/[token]',
		'/my/[token]',
		'/join/[token]',
		'/api/event/[token]'
	])('keeps %s out of search engines and Referer headers', async (routeId) => {
		const headers = await headersFor(routeId);
		expect(headers.get('X-Robots-Tag')).toBe('noindex, nofollow');
		expect(headers.get('Referrer-Policy')).toBe('no-referrer');
	});

	it.each(['/', null])('leaves %s indexable', async (routeId) => {
		const headers = await headersFor(routeId);
		expect(headers.get('X-Robots-Tag')).toBeNull();
		expect(headers.get('Referrer-Policy')).toBeNull();
	});
});
