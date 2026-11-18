import { describe, expect, it } from 'vitest';
import { GET as sitemap } from './sitemap.xml/+server';
import { GET as robots } from './robots.txt/+server';
import { locales } from '$lib/paraglide/runtime';
import { GUIDES } from '$lib/guides';
import { GUIDE_IDS, GUIDE_PATHS } from '$lib/guides/paths';

const ORIGIN = 'https://picko.example';

async function body(handler: typeof sitemap | typeof robots): Promise<string> {
	// Both handlers read nothing but the URL.
	const response = await handler({ url: new URL(ORIGIN) } as never);
	return response.text();
}

describe('sitemap.xml', () => {
	it('lists the homepage and every guide, once per language, on the request host', async () => {
		const xml = await body(sitemap);
		const locs = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1]);
		expect(locs).toEqual([
			`${ORIGIN}/en`,
			`${ORIGIN}/pl`,
			...GUIDE_IDS.flatMap((id) => [
				`${ORIGIN}${GUIDE_PATHS[id].en}`,
				`${ORIGIN}${GUIDE_PATHS[id].pl}`
			])
		]);
	});

	it('links every entry to its page in each language, with English as x-default', async () => {
		const xml = await body(sitemap);
		for (const entry of xml.split('<url>').slice(1)) {
			const loc = entry.match(/<loc>(.*?)<\/loc>/)![1];
			const links = [...entry.matchAll(/hreflang="(.*?)" href="(.*?)"/g)].map((m) => [m[1], m[2]]);
			const [en, pl] = [links[0][1], links[1][1]];
			expect(links).toEqual([
				['en', en],
				['pl', pl],
				['x-default', en]
			]);
			expect([en, pl]).toContain(loc);
		}
	});
});

describe('guides', () => {
	it('have a distinct address per language, under that language', () => {
		const paths = GUIDE_IDS.flatMap((id) => [GUIDE_PATHS[id].en, GUIDE_PATHS[id].pl]);
		expect(new Set(paths).size).toBe(paths.length);
		for (const id of GUIDE_IDS) {
			expect(GUIDE_PATHS[id].en).toMatch(/^\/en\/[a-z-]+$/);
			expect(GUIDE_PATHS[id].pl).toMatch(/^\/pl\/[a-z-]+$/);
		}
	});

	it('are written in every language, with titles and descriptions sized for search results', () => {
		for (const locale of locales) {
			expect(Object.keys(GUIDES[locale]).sort()).toEqual([...GUIDE_IDS].sort());
			for (const guide of Object.values(GUIDES[locale])) {
				expect(guide.seoTitle.length).toBeLessThanOrEqual(70);
				expect(guide.description.length).toBeLessThanOrEqual(165);
				expect(guide.sections.length).toBeGreaterThan(0);
			}
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
