<script lang="ts">
	import { getLocale, localizeHref } from '$lib/paraglide/runtime';
	import { GUIDES, guideRoute, type GuideId } from '$lib/guides';

	interface Props {
		/** Shown under an h2, so each card's title is an h3. */
		ids: GuideId[];
	}

	let { ids }: Props = $props();

	const guides = $derived(GUIDES[getLocale()]);
</script>

<ul class="grid gap-4 sm:grid-cols-2">
	{#each ids as id (id)}
		<li>
			<a
				href={localizeHref(guideRoute(id))}
				class="block h-full rounded-2xl border border-slate-900/5 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md motion-reduce:transition-none motion-reduce:hover:translate-y-0 dark:border-slate-700/50 dark:bg-slate-800/50"
			>
				<h3 class="mb-1 text-base font-semibold text-slate-800 dark:text-white">
					{guides[id].title}
				</h3>
				<p class="text-sm leading-relaxed text-slate-500 dark:text-slate-400">
					{guides[id].summary}
				</p>
			</a>
		</li>
	{/each}
</ul>
