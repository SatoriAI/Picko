<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		animated?: boolean;
		delay?: number;
		children: Snippet;
	}

	let { animated = false, delay = 0, children }: Props = $props();
</script>

<span
	class="chip {animated ? 'chip--animated' : ''}"
	style={animated ? `animation-delay: ${delay}ms` : undefined}
>
	{@render children()}
</span>
