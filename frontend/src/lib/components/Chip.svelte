<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import type { Snippet } from 'svelte';

	interface Props {
		animated?: boolean;
		delay?: number;
		children: Snippet;
	}

	let { animated = false, delay = 0, children }: Props = $props();
</script>

<span
	class="chip {$darkMode ? 'chip--dark' : ''} {animated ? 'chip--animated' : ''}"
	style={animated ? `animation-delay: ${delay}ms` : undefined}
>
	{@render children()}
</span>
