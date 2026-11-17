import { describe, expect, it } from 'vitest';
import type { RequestEvent } from '@sveltejs/kit';
import { handle } from './hooks.server';

// Goes through the exported handle, so dropping the hook from the sequence fails these tests.
async function headersFor(path: string, routeId: string | null): Promise<Headers> {
	const event = {
		request: new Request(`http://localhost${path}`),
		url: new URL(`http://localhost${path}`),
		route: { id: routeId }
	} as RequestEvent;
	const response = await handle({ event, resolve: async () => new Response('ok') });
	return response.headers;
}

describe('handle', () => {
	it.each([
		['/event/abc', '/event/[token]'],
		['/pl/event/abc', '/event/[token]'],
		['/register/abc', '/register/[token]'],
		['/my/abc', '/my/[token]'],
		['/join/abc', '/join/[token]'],
		['/api/event/abc', '/api/event/[token]']
	])('keeps %s out of search engines and Referer headers', async (path, routeId) => {
		const headers = await headersFor(path, routeId);
		expect(headers.get('X-Robots-Tag')).toBe('noindex, nofollow');
		expect(headers.get('Referrer-Policy')).toBe('no-referrer');
	});

	it.each([
		['/', '/'],
		['/nope', null]
	])('leaves %s indexable', async (path, routeId) => {
		const headers = await headersFor(path, routeId);
		expect(headers.get('X-Robots-Tag')).toBeNull();
		expect(headers.get('Referrer-Policy')).toBeNull();
	});

	it.each([
		['http://localhost/pl/', 'http://localhost/pl'],
		['http://localhost/en/?fbclid=abc', 'http://localhost/en?fbclid=abc'],
		['http://localhost/my/abc/', 'http://localhost/my/abc'],
		['http://localhost//', 'http://localhost/'],
		['https://www.picko.world/pl', 'https://picko.world/pl'],
		['https://www.picko.world/', 'https://picko.world/'],
		['https://www.picko.world/pl/?utm_source=x', 'https://picko.world/pl?utm_source=x']
	])('redirects %s to %s', async (url, location) => {
		const event = { request: new Request(url), url: new URL(url) };
		const response = await handle({
			event: event as RequestEvent,
			resolve: async () => new Response('ok')
		});
		expect(response.status).toBe(308);
		expect(response.headers.get('location')).toBe(location);
	});
});
