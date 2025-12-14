<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import type { Snippet } from 'svelte';

	interface Props {
		class?: string;
		children: Snippet;
	}

	let { class: className = '', children }: Props = $props();
</script>

<div
	class="rounded-2xl border p-6 shadow-lg transition-colors sm:p-8 {$darkMode
		? 'border-slate-700/50 bg-slate-800/80 shadow-slate-900/50'
		: 'border-slate-900/5 bg-white shadow-slate-900/5'} {className}"
>
	{@render children()}
</div>
