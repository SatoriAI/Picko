<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import type { Snippet } from 'svelte';

	interface Props {
		icon?: string;
		iconColor?: string;
		children: Snippet;
	}

	let { icon = '✓', iconColor = 'text-emerald-500', children }: Props = $props();
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full border px-3.5 py-2 text-sm font-medium shadow-sm transition-colors {$darkMode
		? 'border-slate-700 bg-slate-800 text-slate-300'
		: 'border-rose-500/15 bg-white text-slate-700'}"
>
	<span class="text-xs {iconColor}">{icon}</span>
	{@render children()}
</span>
