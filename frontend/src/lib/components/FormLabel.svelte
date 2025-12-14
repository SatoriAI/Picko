<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import type { Snippet } from 'svelte';

	interface Props {
		for: string;
		optional?: string;
		children: Snippet;
	}

	let { for: forId, optional, children }: Props = $props();
</script>

<label
	for={forId}
	class="mb-1.5 block text-sm font-medium {$darkMode ? 'text-slate-300' : 'text-slate-600'}"
>
	{@render children()}
	{#if optional}
		<span class="font-normal {$darkMode ? 'text-slate-500' : 'text-slate-400'}">{optional}</span>
	{/if}
</label>
