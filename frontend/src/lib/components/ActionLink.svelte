<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		href: string;
		external?: boolean;
		children: Snippet;
	}

	let { href, external = true, children }: Props = $props();
</script>

<a
	{href}
	target={external ? '_blank' : undefined}
	rel={external ? 'noopener noreferrer' : undefined}
	class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
>
	{@render children()}
</a>
