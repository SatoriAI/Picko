<script lang="ts">
	import { onMount } from 'svelte';
	import { prefersReducedMotion } from 'svelte/motion';
	import { browser } from '$app/environment';

	interface Snowflake {
		id: number;
		x: number;
		drift: number;
		size: number;
		opacity: number;
		duration: number;
		delay: number;
	}

	let snowflakes = $state<Snowflake[]>([]);

	onMount(() => {
		if (!browser) return;

		// Create 40 snowflakes with random properties
		const flakes: Snowflake[] = [];
		for (let i = 0; i < 40; i++) {
			flakes.push({
				id: i,
				x: Math.random() * 100,
				drift: Math.random() * 90 - 45, // -45..45px horizontal drift
				size: Math.random() * 4 + 2, // 2-6px
				opacity: Math.random() * 0.6 + 0.2, // 0.2-0.8
				duration: Math.random() * 8 + 8, // 8-16s
				delay: Math.random() * 10 // 0-10s delay
			});
		}
		snowflakes = flakes;
	});
</script>

<!-- Frozen flakes would only sit at the top edge, so with reduced motion there is no snow at all. This follows the
     setting live, unlike a media query that only stops the animation. -->
<div class="snowfall" aria-hidden="true">
	{#each prefersReducedMotion.current ? [] : snowflakes as flake (flake.id)}
		<div
			class="snowflake"
			style="
				left: {flake.x}%;
				--drift: {flake.drift}px;
				width: {flake.size}px;
				height: {flake.size}px;
				opacity: {flake.opacity};
				animation-duration: {flake.duration}s;
				animation-delay: {flake.delay}s;
			"
		></div>
	{/each}
</div>

<style>
	.snowfall {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
		z-index: 100;
		overflow: hidden;
	}

	.snowflake {
		position: absolute;
		top: -10px;
		background: radial-gradient(circle, white 0%, rgba(255, 255, 255, 0.8) 50%, transparent 100%);
		border-radius: 50%;
		filter: blur(0.5px);
		animation: fall linear infinite;
		will-change: transform;
	}

	@keyframes fall {
		0% {
			transform: translate3d(0, -10px, 0) rotate(0deg);
		}
		100% {
			transform: translate3d(var(--drift), 100vh, 0) rotate(360deg);
		}
	}
</style>
