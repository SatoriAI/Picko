import { describe, expect, it } from 'vitest';
import { GET as sitemap } from './sitemap.xml/+server';
import { GET as robots } from './robots.txt/+server';

const ORIGIN = 'https://picko.example';

async function body(handler: typeof sitemap | typeof robots): Promise<string> {
	// Both handlers read nothing but the URL.
	const response = await handler({ url: new URL(ORIGIN) } as never);
	return response.text();
}

describe('sitemap.xml', () => {
	it('lists only the homepage, once per language, on the request host', async () => {
		const xml = await body(sitemap);
		const locs = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1]);
		expect(locs).toEqual([`${ORIGIN}/en`, `${ORIGIN}/pl`]);
	});

	it('links every entry to each language and to / as x-default', async () => {
		const xml = await body(sitemap);
		for (const entry of xml.split('<url>').slice(1)) {
			const links = [...entry.matchAll(/hreflang="(.*?)" href="(.*?)"/g)].map((m) => [m[1], m[2]]);
			expect(links).toEqual([
				['en', `${ORIGIN}/en`],
				['pl', `${ORIGIN}/pl`],
				['x-default', `${ORIGIN}/`]
			]);
		}
	});
});

describe('robots.txt', () => {
	it('allows crawling and points at the sitemap by absolute URL', async () => {
		const text = await body(robots);
		expect(text).toContain('User-agent: *\nDisallow:\n');
		expect(text).toContain(`Sitemap: ${ORIGIN}/sitemap.xml`);
	});
});
