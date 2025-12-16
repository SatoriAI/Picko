<script lang="ts">
	// Christmas fairy lights that twinkle
	const lights = [
		{ color: '#ef4444', delay: 0 }, // red
		{ color: '#22c55e', delay: 0.5 }, // green
		{ color: '#eab308', delay: 1 }, // yellow
		{ color: '#3b82f6', delay: 1.5 }, // blue
		{ color: '#ef4444', delay: 2 }, // red
		{ color: '#22c55e', delay: 2.5 }, // green
		{ color: '#eab308', delay: 3 }, // yellow
		{ color: '#3b82f6', delay: 3.5 }, // blue
		{ color: '#ef4444', delay: 0.25 }, // red
		{ color: '#22c55e', delay: 0.75 }, // green
		{ color: '#eab308', delay: 1.25 }, // yellow
		{ color: '#3b82f6', delay: 1.75 }, // blue
		{ color: '#ef4444', delay: 2.25 }, // red
		{ color: '#22c55e', delay: 2.75 }, // green
		{ color: '#eab308', delay: 3.25 }, // yellow
		{ color: '#3b82f6', delay: 3.75 } // blue
	];
</script>

<div class="lights-container" aria-hidden="true">
	<svg class="lights-wire" viewBox="0 0 100 8" preserveAspectRatio="none">
		<path
			d="M0,4 Q6.25,7 12.5,4 Q18.75,1 25,4 Q31.25,7 37.5,4 Q43.75,1 50,4 Q56.25,7 62.5,4 Q68.75,1 75,4 Q81.25,7 87.5,4 Q93.75,1 100,4"
			fill="none"
			stroke="currentColor"
			stroke-width="0.3"
			class="wire"
		/>
	</svg>
	<div class="lights">
		{#each lights as light, i (i)}
			<div
				class="light"
				style="
					--color: {light.color};
					--delay: {light.delay}s;
					left: calc({(i / (lights.length - 1)) * 100}% - 6px);
					top: {i % 2 === 0 ? '2px' : '0px'};
				"
			>
				<div class="bulb"></div>
				<div class="glow"></div>
			</div>
		{/each}
	</div>
</div>

<style>
	.lights-container {
		position: absolute;
		bottom: -12px;
		left: 0;
		right: 0;
		height: 24px;
		z-index: 40;
		overflow: visible;
	}

	.lights-wire {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 8px;
	}

	.wire {
		color: #1e293b;
	}

	:global(.dark) .wire {
		color: #475569;
	}

	.lights {
		position: absolute;
		top: 2px;
		left: 0;
		right: 0;
		height: 20px;
	}

	.light {
		position: absolute;
		width: 12px;
		height: 16px;
	}

	.bulb {
		width: 10px;
		height: 12px;
		background: var(--color);
		border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
		position: relative;
		box-shadow: 0 0 4px var(--color);
		animation: twinkle 2s ease-in-out infinite;
		animation-delay: var(--delay);
	}

	.bulb::before {
		content: '';
		position: absolute;
		top: -3px;
		left: 50%;
		transform: translateX(-50%);
		width: 6px;
		height: 4px;
		background: #374151;
		border-radius: 2px 2px 0 0;
	}

	.glow {
		position: absolute;
		top: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 20px;
		height: 20px;
		background: radial-gradient(circle, var(--color) 0%, transparent 70%);
		opacity: 0.4;
		animation: twinkle 2s ease-in-out infinite;
		animation-delay: var(--delay);
		pointer-events: none;
	}

	@keyframes twinkle {
		0%,
		100% {
			opacity: 1;
			filter: brightness(1);
		}
		50% {
			opacity: 0.5;
			filter: brightness(0.6);
		}
	}

	/* Reduce motion for users who prefer it */
	@media (prefers-reduced-motion: reduce) {
		.bulb,
		.glow {
			animation: none;
		}
	}
</style>
