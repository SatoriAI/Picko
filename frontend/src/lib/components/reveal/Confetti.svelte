<script lang="ts">
	interface Props {
		show: boolean;
		pieceCount?: number;
	}

	let { show, pieceCount = 50 }: Props = $props();

	const COLORS = ['#f97316', '#ec4899', '#eab308', '#22c55e', '#3b82f6', '#a855f7'];

	let pieces = $state<Array<{ id: number; x: number; color: string; delay: number }>>([]);

	$effect(() => {
		if (show) {
			pieces = Array.from({ length: pieceCount }, (_, i) => ({
				id: i,
				x: Math.random() * 100,
				color: COLORS[Math.floor(Math.random() * COLORS.length)],
				delay: Math.random() * 0.5
			}));
		}
	});
</script>

{#if show}
	<div class="pointer-events-none absolute inset-0 overflow-hidden">
		{#each pieces as piece (piece.id)}
			<div
				class="confetti-piece absolute"
				style="
					left: {piece.x}%;
					background-color: {piece.color};
					animation-delay: {piece.delay}s;
				"
			></div>
		{/each}
	</div>
{/if}

<style>
	@keyframes confetti-fall {
		0% {
			transform: translateY(-20px) rotate(0deg);
			opacity: 1;
		}
		100% {
			transform: translateY(400px) rotate(720deg);
			opacity: 0;
		}
	}

	.confetti-piece {
		width: 10px;
		height: 10px;
		border-radius: 2px;
		animation: confetti-fall 3s ease-out forwards;
	}
</style>
