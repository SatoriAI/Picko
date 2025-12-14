<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import Header from './Header.svelte';
	import Footer from './Footer.svelte';
	import type { Snippet } from 'svelte';

	interface Props {
		isHeaderLink?: boolean;
		children: Snippet;
	}

	let { isHeaderLink = false, children }: Props = $props();
</script>

<div
	class="min-h-screen font-[Outfit,system-ui,sans-serif] transition-colors duration-300 {$darkMode
		? 'bg-slate-900 text-slate-100'
		: 'bg-gradient-to-br from-amber-50 via-blue-50 to-orange-50 text-slate-800'}"
>
	<Header isLink={isHeaderLink} />

	<main class="px-4 pb-12 sm:px-6">
		{@render children()}
	</main>

	<Footer />
</div>
