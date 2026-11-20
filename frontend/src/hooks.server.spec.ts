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
		['http://localhost/pl/', '/pl'],
		['http://localhost/en/?fbclid=abc', '/en?fbclid=abc'],
		['http://localhost/my/abc/', '/my/abc'],
		['http://localhost//', '/'],
		['https://www.picko.world/pl', 'https://picko.world/pl'],
		['https://www.picko.world/', 'https://picko.world/'],
		['https://www.picko.world/pl/?utm_source=x', 'https://picko.world/pl?utm_source=x']
	])('redirects %s to %s', async (url, location) => {
		const response = await handle({
			event: pageEvent(url),
			resolve: async () => new Response('ok')
		});
		expect(response.status).toBe(308);
		expect(response.headers.get('location')).toBe(location);
	});

	it.each([
		['an API call', pageEvent('https://www.picko.world/api/event', { method: 'POST' })],
		[
			'a data request',
			{ ...pageEvent('https://www.picko.world/pl'), isDataRequest: true } as RequestEvent
		]
	])('serves %s on www instead of redirecting it cross-origin', async (_, event) => {
		const response = await handle({ event, resolve: async () => new Response('ok') });
		expect(response.status).toBe(200);
	});

	const html = () => new Response('<p>ok</p>', { headers: { 'content-type': 'text/html' } });

	it.each(['http://localhost/', 'http://localhost/my/abc'])(
		'marks %s as varying by language, which it reads from the cookie or browser',
		async (url) => {
			const response = await handle({ event: pageEvent(url), resolve: async () => html() });
			expect(response.headers.get('vary')).toBe('Cookie, Accept-Language');
		}
	);

	it('adds Cookie to the Vary of the redirect from / without repeating Accept-Language', async () => {
		const request = new Request('http://localhost/', {
			headers: { 'Sec-Fetch-Dest': 'document', 'Accept-Language': 'pl' }
		});
		const event = { ...pageEvent('http://localhost/'), request } as RequestEvent;
		const response = await handle({ event, resolve: async () => html() });
		expect(response.status).toBe(307);
		expect(response.headers.get('vary')).toBe('Accept-Language, Cookie');
	});

	it.each([
		['a page whose address names its language', 'http://localhost/pl', html],
		[
			'a file that is the same in every language',
			'http://localhost/sitemap.xml',
			() => new Response('<urlset/>', { headers: { 'content-type': 'application/xml' } })
		]
	])('leaves Vary off %s', async (_, url, resolve) => {
		const response = await handle({ event: pageEvent(url), resolve: async () => resolve() });
		expect(response.headers.get('vary')).toBeNull();
	});
});

function pageEvent(url: string, init?: RequestInit): RequestEvent {
	return {
		request: new Request(url, init),
		url: new URL(url),
		route: { id: null },
		isDataRequest: false
	} as RequestEvent;
}
