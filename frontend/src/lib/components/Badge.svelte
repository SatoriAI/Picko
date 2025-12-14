<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		icon?: string;
		iconColor?: string;
		children: Snippet;
	}

	let { icon = '✓', iconColor = 'text-emerald-500', children }: Props = $props();
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full border border-rose-500/15 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
>
	<span class="text-xs {iconColor}">{icon}</span>
	{@render children()}
</span>
