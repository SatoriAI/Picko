<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { page } from '$app/state';
	import { getLocale, localizeHref } from '$lib/paraglide/runtime';
	import { GUIDE_IDS, GUIDES, GUIDES_PUBLISHED, guideRoute } from '$lib/guides';
	import { localizedPage } from '$lib/seo';
	import { PageLayout, SeoHead, GuideCards } from '$lib/components';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const locale = getLocale();
	const guide = $derived(GUIDES[locale][data.id]);
	const route = $derived(guideRoute(data.id));
	const homeUrl = $derived(localizedPage(page.url.origin, '/', locale));

	const structuredData = $derived([
		{
			'@context': 'https://schema.org',
			'@type': 'Article',
			headline: guide.title,
			description: guide.description,
			inLanguage: locale,
			url: localizedPage(page.url.origin, route, locale),
			image: new URL(`/og-${locale}.png`, page.url.origin).href,
			datePublished: GUIDES_PUBLISHED,
			author: { '@type': 'Person', name: 'Dawid Hanrahan', url: 'https://dawidhanrahan.com' },
			publisher: { '@type': 'Organization', name: m.app_name(), url: homeUrl }
		},
		{
			'@context': 'https://schema.org',
			'@type': 'BreadcrumbList',
			itemListElement: [
				{ '@type': 'ListItem', position: 1, name: m.app_name(), item: homeUrl },
				{
					'@type': 'ListItem',
					position: 2,
					name: guide.title,
					item: localizedPage(page.url.origin, route, locale)
				}
			]
		}
	]);
</script>

<SeoHead
	{route}
	title={guide.seoTitle}
	description={guide.description}
	ogType="article"
	{structuredData}
/>

<PageLayout>
	<article class="mx-auto max-w-3xl py-8 sm:py-12">
		<h1
			class="mb-6 text-3xl font-bold leading-tight tracking-tight text-slate-800 sm:text-4xl dark:text-white"
		>
			{guide.title}
		</h1>

		<div
			class="prose prose-slate max-w-none dark:prose-invert prose-headings:tracking-tight prose-a:text-rose-600 dark:prose-a:text-rose-400"
		>
			{#each guide.intro as paragraph, i (i)}
				<p class={i === 0 ? 'lead' : ''}>{paragraph}</p>
			{/each}

			{#each guide.sections as section (section.heading)}
				<h2>{section.heading}</h2>
				{#each section.paragraphs as paragraph, i (i)}
					<p>{paragraph}</p>
				{/each}
				{#if section.list}
					<ul>
						{#each section.list as item, i (i)}
							<li>{item}</li>
						{/each}
					</ul>
				{/if}
			{/each}
		</div>

		<aside
			class="mt-10 rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-sm dark:border-rose-900/50 dark:bg-slate-800/80"
		>
			<h2 class="mb-2 text-xl font-bold text-slate-800 dark:text-white">{m.guide_cta_title()}</h2>
			<p class="mx-auto mb-5 max-w-md text-slate-600 dark:text-slate-300">{m.guide_cta_desc()}</p>
			<a
				href={localizeHref('/')}
				class="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-orange-400 to-rose-500 px-6 py-3.5 font-semibold text-white shadow-md shadow-rose-500/30 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-rose-500/40 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
			>
				{m.guide_cta_button()}
			</a>
		</aside>

		<section class="mt-12" aria-labelledby="more-guides">
			<h2
				id="more-guides"
				class="mb-4 text-xl font-bold tracking-tight text-slate-800 dark:text-white"
			>
				{m.guide_more_title()}
			</h2>
			<GuideCards ids={GUIDE_IDS.filter((id) => id !== data.id)} />
		</section>
	</article>
</PageLayout>
