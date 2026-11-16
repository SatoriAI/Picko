<script lang="ts">
	import '@fontsource-variable/outfit';
	import outfitLatin from '@fontsource-variable/outfit/files/outfit-latin-wght-normal.woff2?url';
	import './layout.css';
	import { browser } from '$app/environment';
	import { darkMode } from '$lib/stores/theme';

	let { children } = $props();

	$effect(() => {
		if (!browser) return;
		document.documentElement.classList.toggle('dark', $darkMode);
	});
</script>

<svelte:head>
	<!-- Every page draws its text in Outfit, so fetch it with the HTML rather than after the CSS is parsed. Polish
	     pages also need the latin-ext file, which the browser discovers through unicode-range. -->
	<link rel="preload" href={outfitLatin} as="font" type="font/woff2" crossorigin="anonymous" />
</svelte:head>

{@render children()}
