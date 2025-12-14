<script lang="ts">
	import { getLocale, setLocale, type Locale } from '$lib/paraglide/runtime';
	import { darkMode } from '$lib/stores/theme';

	const locales: Array<{ code: Locale; flag: string; label: string }> = [
		{ code: 'en', flag: '🇬🇧', label: 'English' },
		{ code: 'pl', flag: '🇵🇱', label: 'Polski' }
	];

	let currentLocale = $derived(getLocale());
</script>

<div
	class="flex items-center gap-1 rounded-xl p-1 shadow-sm transition-colors {$darkMode
		? 'bg-slate-800'
		: 'bg-white'}"
>
	{#each locales as { code, flag, label }}
		<button
			type="button"
			class="flex cursor-pointer items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all {currentLocale ===
			code
				? 'bg-rose-500 text-white shadow-sm'
				: $darkMode
					? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200'
					: 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'}"
			onclick={() => setLocale(code)}
		>
			<span>{flag}</span>
			<span class="hidden sm:inline">{label}</span>
		</button>
	{/each}
</div>
