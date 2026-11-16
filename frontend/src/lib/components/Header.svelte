<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import ThemeToggle from './ThemeToggle.svelte';
	import LanguageSwitcher from './LanguageSwitcher.svelte';
	import { CHRISTMAS_THEME } from '$lib/stores/christmas';
	import { ChristmasLights, SantaHat } from './christmas';
</script>

<header
	class="sticky top-0 z-50 border-b border-slate-900/5 bg-amber-50/85 px-4 py-4 backdrop-blur-md transition-colors duration-300 dark:border-slate-700/50 dark:bg-slate-900/85 sm:px-6"
>
	<div class="mx-auto flex max-w-5xl items-center justify-between">
		<!-- Straight to this language's homepage, so following it never costs the redirect that `/` answers with. -->
		<a href={localizeHref('/')} class="flex items-center gap-2">
			<span class="relative text-2xl drop-shadow-sm" aria-hidden="true">
				🎁
				{#if CHRISTMAS_THEME}
					<SantaHat />
				{/if}
			</span>
			<span class="text-xl font-bold tracking-tight text-rose-500">{m.app_name()}</span>
		</a>
		<div class="flex items-center gap-3">
			<ThemeToggle />
			<LanguageSwitcher />
		</div>
	</div>
	{#if CHRISTMAS_THEME}
		<ChristmasLights />
	{/if}
</header>
