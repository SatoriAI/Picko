<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import { SunIcon, MoonIcon } from './icons';
</script>

<button
	type="button"
	onclick={() => darkMode.toggle()}
	class="flex h-9 w-9 items-center justify-center rounded-lg transition-all {$darkMode
		? 'bg-slate-800 text-yellow-400 hover:bg-slate-700'
		: 'bg-white text-slate-600 shadow-sm hover:bg-slate-50'}"
	aria-label="Toggle dark mode"
>
	{#if $darkMode}
		<SunIcon />
	{:else}
		<MoonIcon />
	{/if}
</button>
