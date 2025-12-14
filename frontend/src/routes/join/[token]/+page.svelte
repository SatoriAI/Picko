<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { formatDateLong } from '$lib/utils/date';
	import { PageLayout, Card } from '$lib/components';
	import type { AssignmentData } from './+page';

	// Props from loader
	let { data } = $props();
	const assignment: AssignmentData = data.assignment;

	// Reveal state
	let isRevealed = $state(false);
	let isShaking = $state(false);
	let showConfetti = $state(false);
	let confettiPieces = $state<Array<{ id: number; x: number; color: string; delay: number }>>([]);

	// Generate confetti pieces
	function generateConfetti() {
		const colors = ['#f97316', '#ec4899', '#eab308', '#22c55e', '#3b82f6', '#a855f7'];
		confettiPieces = Array.from({ length: 50 }, (_, i) => ({
			id: i,
			x: Math.random() * 100,
			color: colors[Math.floor(Math.random() * colors.length)],
			delay: Math.random() * 0.5
		}));
	}

	// Handle the reveal button click
	async function handleReveal() {
		// Start shaking animation
		isShaking = true;

		// After shake, reveal
		setTimeout(() => {
			isShaking = false;
			isRevealed = true;
			showConfetti = true;
			generateConfetti();

			// Hide confetti after animation
			setTimeout(() => {
				showConfetti = false;
			}, 4000);
		}, 800);
	}
</script>

<svelte:head>
	<title>{m.join_page_title()} - {m.app_name()}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<div class="flex min-h-[70vh] flex-col items-center justify-center py-8">
		<!-- Event name badge -->
		<div
			class="mb-6 rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
		>
			🎄 {assignment.event.name}
		</div>

		<!-- Main reveal area -->
		<div class="relative w-full max-w-md">
			<!-- Confetti -->
			{#if showConfetti}
				<div class="pointer-events-none absolute inset-0 overflow-hidden">
					{#each confettiPieces as piece (piece.id)}
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

			{#if !isRevealed}
				<!-- Gift box (pre-reveal) -->
				<div class="flex flex-col items-center">
					<div
						class="gift-box mb-8 flex h-48 w-48 items-center justify-center rounded-3xl shadow-2xl {isShaking
							? 'animate-shake'
							: 'animate-float'}"
						style="background: linear-gradient(135deg, #f97316 0%, #ec4899 100%);"
					>
						<!-- Gift ribbon -->
						<div class="relative">
							<div
								class="absolute left-1/2 top-1/2 h-48 w-4 -translate-x-1/2 -translate-y-1/2 bg-yellow-300 opacity-80"
							></div>
							<div
								class="absolute left-1/2 top-1/2 h-4 w-48 -translate-x-1/2 -translate-y-1/2 bg-yellow-300 opacity-80"
							></div>
							<!-- Bow -->
							<div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-6xl">
								🎁
							</div>
						</div>
					</div>

					<!-- Greeting -->
					<h1
						class="mb-3 text-center text-2xl font-bold text-slate-800 sm:text-3xl dark:text-white"
					>
						{m.join_greeting({ name: assignment.giver_name })}
					</h1>
					<p class="mb-8 text-center text-slate-500 dark:text-slate-400">
						{m.join_ready_question()}
					</p>

					<!-- Reveal button -->
					<button
						onclick={handleReveal}
						disabled={isShaking}
						class="group relative cursor-pointer overflow-hidden rounded-2xl px-8 py-4 text-lg font-bold text-white shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl disabled:cursor-wait"
						style="background: linear-gradient(135deg, #f97316 0%, #ec4899 100%);"
					>
						<span class="relative z-10 flex items-center gap-2">
							<span class="text-2xl">✨</span>
							{m.join_reveal_button()}
							<span class="text-2xl">✨</span>
						</span>
						<div
							class="absolute inset-0 -translate-x-full bg-white/20 transition-transform group-hover:translate-x-full"
						></div>
					</button>
				</div>
			{:else}
				<!-- Revealed state -->
				<div class="flex flex-col items-center">
					<!-- Success icon -->
					<div
						class="mb-6 flex h-20 w-20 animate-bounce-in items-center justify-center rounded-full text-5xl shadow-lg"
						style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);"
					>
						🎉
					</div>

					<!-- The big reveal card -->
					<Card class="w-full animate-scale-in p-8 text-center">
						<p class="mb-2 text-sm uppercase tracking-wide text-slate-500 dark:text-slate-400">
							{m.join_you_are_gifting()}
						</p>
						<h2
							class="mb-4 bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-4xl font-extrabold text-transparent sm:text-5xl"
						>
							{assignment.receiver_name}
						</h2>

						<!-- Divider -->
						<div class="my-6 flex items-center gap-4">
							<div class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></div>
							<span class="text-2xl">🎁</span>
							<div class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></div>
						</div>

						<!-- Event details -->
						<div class="space-y-3 text-sm">
							{#if assignment.event.date}
								<div
									class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-300"
								>
									<span>📅</span>
									<span
										>{m.join_event_date()}:
										<strong>{formatDateLong(assignment.event.date, getLocale())}</strong></span
									>
								</div>
							{/if}
							{#if assignment.event.max_amount}
								<div
									class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-300"
								>
									<span>💰</span>
									<span
										>{m.join_budget()}:
										<strong
											>{assignment.event.max_amount} {assignment.event.currency ?? 'PLN'}</strong
										></span
									>
								</div>
							{/if}
						</div>
					</Card>

					<!-- Fun reminder -->
					<p
						class="mt-6 flex items-center gap-2 text-center text-sm text-slate-500 dark:text-slate-400"
					>
						<span>🤫</span>
						{m.join_keep_secret()}
					</p>
				</div>
			{/if}
		</div>
	</div>
</PageLayout>

<style>
	/* Floating animation for the gift box */
	@keyframes float {
		0%,
		100% {
			transform: translateY(0px);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	.animate-float {
		animation: float 3s ease-in-out infinite;
	}

	/* Shake animation */
	@keyframes shake {
		0%,
		100% {
			transform: translateX(0) rotate(0deg);
		}
		10%,
		30%,
		50%,
		70%,
		90% {
			transform: translateX(-5px) rotate(-2deg);
		}
		20%,
		40%,
		60%,
		80% {
			transform: translateX(5px) rotate(2deg);
		}
	}

	.animate-shake {
		animation: shake 0.8s ease-in-out;
	}

	/* Bounce in for the success icon */
	@keyframes bounce-in {
		0% {
			transform: scale(0);
			opacity: 0;
		}
		50% {
			transform: scale(1.2);
		}
		100% {
			transform: scale(1);
			opacity: 1;
		}
	}

	.animate-bounce-in {
		animation: bounce-in 0.5s ease-out forwards;
	}

	/* Scale in for the card */
	@keyframes scale-in {
		0% {
			transform: scale(0.8);
			opacity: 0;
		}
		100% {
			transform: scale(1);
			opacity: 1;
		}
	}

	:global(.animate-scale-in) {
		animation: scale-in 0.4s ease-out 0.2s forwards;
		opacity: 0;
	}

	/* Confetti animation */
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
