<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { page } from '$app/state';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { localizedPage, pageAlternates } from '$lib/seo';

	interface Props {
		/** The app route, e.g. `/` or `/guides/work`; the public address per language is derived from it. */
		route: string;
		title: string;
		description: string;
		ogType?: 'website' | 'article';
		/** JSON-LD objects; each `url` should be the canonical address. */
		structuredData?: object[];
	}

	let { route, title, description, ogType = 'website', structuredData = [] }: Props = $props();

	const OG_LOCALES = { en: 'en_US', pl: 'pl_PL' } as const;
	const locale = getLocale();
	const canonical = $derived(localizedPage(page.url.origin, route, locale));
	const ogImage = $derived(new URL(`/og-${locale}.png`, page.url.origin).href);
	// `<` is escaped so no string can close the tag, and the closing tag is split so it doesn't end this component's
	// own <script> block.
	const structuredDataTags = $derived(
		structuredData
			.map(
				(data) =>
					`<script type="application/ld+json">${JSON.stringify(data).replace(/</g, '\\u003c')}</` +
					'script>'
			)
			.join('')
	);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<link rel="canonical" href={canonical} />
	{#each pageAlternates(page.url.origin, route) as { hreflang, href } (hreflang)}
		<link rel="alternate" {hreflang} {href} />
	{/each}

	<meta property="og:type" content={ogType} />
	<meta property="og:site_name" content={m.app_name()} />
	<meta property="og:title" content={title} />
	<meta property="og:description" content={description} />
	<meta property="og:url" content={canonical} />
	<meta property="og:image" content={ogImage} />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta property="og:image:alt" content={m.og_image_alt()} />
	<meta property="og:locale" content={OG_LOCALES[locale]} />
	{#each locales.filter((l) => l !== locale) as alternate (alternate)}
		<meta property="og:locale:alternate" content={OG_LOCALES[alternate]} />
	{/each}
	<meta name="twitter:card" content="summary_large_image" />

	<!-- eslint-disable-next-line svelte/no-at-html-tags -- JSON-LD built from our own strings, `<` escaped -->
	{@html structuredDataTags}
</svelte:head>
