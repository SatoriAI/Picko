<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		class?: string;
		children: Snippet;
	}

	let { class: className = '', children }: Props = $props();
</script>

<div
	class="rounded-2xl border border-slate-900/5 bg-white p-6 shadow-lg shadow-slate-900/5 transition-colors dark:border-slate-700/50 dark:bg-slate-800/80 dark:shadow-slate-900/50 sm:p-8 {className}"
>
	{@render children()}
</div>
