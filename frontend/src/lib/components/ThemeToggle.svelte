<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import { SunIcon, MoonIcon } from './icons';
</script>

<button
	type="button"
	onclick={() => darkMode.toggle()}
	class="flex h-9 w-9 items-center justify-center rounded-lg bg-white text-slate-600 shadow-sm transition-all hover:bg-slate-50 dark:bg-slate-800 dark:text-yellow-400 dark:hover:bg-slate-700"
	aria-label="Toggle dark mode"
>
	{#if $darkMode}
		<SunIcon />
	{:else}
		<MoonIcon />
	{/if}
</button>
