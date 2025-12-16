<script lang="ts">
	import Header from './Header.svelte';
	import Footer from './Footer.svelte';
	import type { Snippet } from 'svelte';
	import { CHRISTMAS_THEME } from '$lib/stores/christmas';
	import { Snowfall } from './christmas';

	interface Props {
		isHeaderLink?: boolean;
		children: Snippet;
	}

	let { isHeaderLink = false, children }: Props = $props();
</script>

{#if CHRISTMAS_THEME}
	<Snowfall />
{/if}

<div
	class="flex min-h-screen flex-col bg-gradient-to-br from-amber-50 via-blue-50 to-orange-50 font-[Outfit,system-ui,sans-serif] text-slate-800 transition-colors duration-300 dark:bg-none dark:bg-slate-900 dark:text-slate-100"
	class:christmas-theme={CHRISTMAS_THEME}
>
	<Header isLink={isHeaderLink} />

	<main class="flex-1 px-4 pb-12 sm:px-6">
		{@render children()}
	</main>

	<Footer />
</div>
