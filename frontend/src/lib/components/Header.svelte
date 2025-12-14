<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { resolve } from '$app/paths';
	import ThemeToggle from './ThemeToggle.svelte';
	import LanguageSwitcher from './LanguageSwitcher.svelte';

	interface Props {
		isLink?: boolean;
	}

	let { isLink = false }: Props = $props();
</script>

<header
	class="sticky top-0 z-50 border-b border-slate-900/5 bg-amber-50/85 px-4 py-4 backdrop-blur-md transition-colors duration-300 dark:border-slate-700/50 dark:bg-slate-900/85 sm:px-6"
>
	<div class="mx-auto flex max-w-5xl items-center justify-between">
		<svelte:element
			this={isLink ? 'a' : 'div'}
			href={isLink ? resolve('/') : undefined}
			class="flex items-center gap-2"
		>
			<span class="text-2xl drop-shadow-sm">🎁</span>
			<span class="text-xl font-bold tracking-tight text-rose-500">{m.app_name()}</span>
		</svelte:element>
		<div class="flex items-center gap-3">
			<ThemeToggle />
			<LanguageSwitcher />
		</div>
	</div>
</header>
