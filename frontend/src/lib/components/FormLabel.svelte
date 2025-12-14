<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		for: string;
		optional?: string;
		children: Snippet;
	}

	let { for: forId, optional, children }: Props = $props();
</script>

<label for={forId} class="mb-1.5 block text-sm font-medium text-slate-600 dark:text-slate-300">
	{@render children()}
	{#if optional}
		<span class="font-normal text-slate-400 dark:text-slate-500">{optional}</span>
	{/if}
</label>
