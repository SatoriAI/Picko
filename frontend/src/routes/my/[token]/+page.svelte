<script lang="ts">
	import { resolve } from '$app/paths';
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { formatDateLong } from '$lib/utils/date';
	import { createFeedbackState } from '$lib/utils/feedback.svelte';
	import { onMount, onDestroy } from 'svelte';
	import { PageLayout, Card, Button, CheckIcon, CopyIcon } from '$lib/components';
	import type { MyStatusData } from './+page';

	// Props from loader
	let { data } = $props();
	const status: MyStatusData = data;

	// Countdown state
	let countdown = $state({ days: 0, hours: 0, minutes: 0, seconds: 0 });
	let countdownInterval: ReturnType<typeof setInterval> | null = null;
	let isLoadingDraw = $state(false);

	// Reveal animation state
	let isRevealed = $state(false);
	let isShaking = $state(false);
	let showConfetti = $state(false);
	let confettiPieces = $state<Array<{ id: number; x: number; color: string; delay: number }>>([]);

	// Feedback states
	const linkCopied = createFeedbackState(2500);

	// Derived states
	let deadlinePassed = $derived(new Date(status.event.registration_deadline) <= new Date());
	let drawFailed = $derived(deadlinePassed && !status.event.is_draw_complete && !status.assignment);
	let myLink = $derived(typeof window !== 'undefined' ? window.location.href : '');

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
	function handleReveal() {
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

	// Calculate countdown
	function updateCountdown() {
		const now = new Date().getTime();
		const deadline = new Date(status.event.registration_deadline).getTime();
		const diff = deadline - now;

		if (diff <= 0) {
			countdown = { days: 0, hours: 0, minutes: 0, seconds: 0 };
			if (countdownInterval) {
				clearInterval(countdownInterval);
				countdownInterval = null;
				// Show loading state and reload to get assignment
				isLoadingDraw = true;
				setTimeout(() => {
					window.location.reload();
				}, 1500);
			}
			return;
		}

		countdown = {
			days: Math.floor(diff / (1000 * 60 * 60 * 24)),
			hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
			minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
			seconds: Math.floor((diff % (1000 * 60)) / 1000)
		};
	}

	onMount(() => {
		updateCountdown();
		if (!deadlinePassed && !status.assignment) {
			countdownInterval = setInterval(updateCountdown, 1000);
		}
	});

	onDestroy(() => {
		if (countdownInterval) {
			clearInterval(countdownInterval);
		}
	});

	async function copyMyLink() {
		try {
			await navigator.clipboard.writeText(myLink);
			linkCopied.trigger();
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	function getCalendarUrl() {
		if (!status.event.date) return null;
		const date = new Date(status.event.date);
		const dateStr = date.toISOString().replace(/-|:|\.\d+/g, '').slice(0, 8);
		const title = encodeURIComponent(status.event.name);
		return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dateStr}/${dateStr}`;
	}
</script>

<svelte:head>
	<title>{m.my_status_title()}: {status.event.name}</title>
</svelte:head>

<PageLayout isHeaderLink>
	{#if isLoadingDraw}
		<!-- Loading state when countdown reaches 0 -->
		<div class="flex min-h-[70vh] flex-col items-center justify-center py-8">
			<div class="mb-6 h-12 w-12 animate-spin rounded-full border-4 border-orange-200 border-t-orange-500"></div>
			<p class="text-lg font-medium text-slate-600 dark:text-slate-300">
				{m.my_loading_draw()}
			</p>
		</div>
	{:else if drawFailed}
		<!-- Draw failed - not enough participants -->
		<div class="flex min-h-[70vh] flex-col items-center justify-center py-8">
			<div class="mx-auto max-w-md text-center">
				<div class="mb-6 text-6xl">😔</div>
				<h1 class="mb-3 text-2xl font-bold text-slate-800 dark:text-white">
					{m.my_draw_failed_title()}
				</h1>
				<p class="mb-2 text-slate-500 dark:text-slate-400">
					{m.my_draw_failed_desc()}
				</p>
				<p class="mb-8 text-sm text-slate-400 dark:text-slate-500">
					{m.my_draw_failed_contact()}
				</p>
				<a
					href={resolve(`/event/${status.event.id}`)}
					target="_blank"
					rel="noopener noreferrer"
					class="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-5 py-3 font-medium text-slate-700 transition-colors hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
				>
					<span>👥</span>
					{m.my_view_event_button()}
				</a>
			</div>
		</div>
	{:else if status.assignment}
		<!-- Assignment Ready - Show Gift Box Reveal -->
		<div class="flex min-h-[70vh] flex-col items-center justify-center py-8">
			<!-- Event name badge -->
			<div
				class="mb-6 rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
			>
				🎄 {status.event.name}
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
							{m.my_greeting({ name: status.participant_name })}
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
								{status.assignment.receiver_name}
							</h2>

							<!-- Divider -->
							<div class="my-6 flex items-center gap-4">
								<div class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></div>
								<span class="text-2xl">🎁</span>
								<div class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></div>
							</div>

							<!-- Event details -->
							<div class="space-y-3 text-sm">
								{#if status.event.date}
									<div
										class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-300"
									>
										<span>📅</span>
										<span>
											{m.join_event_date()}:
											<strong>{formatDateLong(status.event.date, getLocale())}</strong>
										</span>
									</div>
								{/if}
								{#if status.event.max_amount}
									<div
										class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-300"
									>
										<span>💰</span>
										<span>
											{m.join_budget()}:
											<strong>{status.event.max_amount} {status.event.currency ?? 'PLN'}</strong>
										</span>
									</div>
								{/if}
							</div>

							<!-- Wishlist -->
							{#if status.assignment.receiver_wishlist}
								<div class="mt-6 rounded-xl bg-slate-50 p-4 dark:bg-slate-700/50">
									<p
										class="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
									>
										{m.join_wishlist_title()}
									</p>
									<div class="flex flex-wrap justify-center gap-2">
										{#each status.assignment.receiver_wishlist
											.split(',')
											.map((w) => w.trim()) as wish (wish)}
											{#if wish}
												<span
													class="rounded-full bg-white px-3 py-1 text-sm text-slate-700 shadow-sm dark:bg-slate-600 dark:text-slate-200"
												>
													🎁 {wish}
												</span>
											{/if}
										{/each}
									</div>
								</div>
							{/if}
						</Card>

						<!-- Secret reminder -->
						<p
							class="mt-4 mb-6 flex items-center gap-2 text-center text-sm text-slate-500 dark:text-slate-400"
						>
							<span>🤫</span>
							{m.join_keep_secret()}
						</p>

						<!-- Action links -->
						<div class="flex flex-wrap items-center justify-center gap-3">
							{#if status.event.date}
								{@const calendarUrl = getCalendarUrl()}
								{#if calendarUrl}
									<a
										href={calendarUrl}
										target="_blank"
										rel="noopener noreferrer"
										class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
									>
										<span>📅</span>
										{m.my_add_to_calendar()}
									</a>
								{/if}
							{/if}
							<a
								href={resolve(`/event/${status.event.id}`)}
								target="_blank"
								rel="noopener noreferrer"
								class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
							>
								<span>👥</span>
								{m.my_view_event_button()}
							</a>
						</div>
					</div>
				{/if}
			</div>
		</div>
	{:else}
		<!-- Waiting for Draw -->
		<div class="flex min-h-[70vh] flex-col items-center justify-center py-8">
			<div class="mx-auto w-full max-w-lg px-4">
				<!-- Header -->
				<div class="mb-10 text-center">
					<h1 class="mb-2 text-2xl font-bold text-slate-800 sm:text-3xl dark:text-white">
						{m.my_greeting({ name: status.participant_name })}
					</h1>
					<p class="text-slate-500 dark:text-slate-400">
						{m.my_waiting_subtitle({ event: status.event.name })}
					</p>
				</div>

				<!-- Countdown Timer - Standalone -->
				<div class="mb-4 text-center">
					<h3 class="mb-6 text-sm font-medium uppercase tracking-widest text-slate-400 dark:text-slate-500">
						{m.countdown_title()}
					</h3>
					<div class="grid grid-cols-4 gap-4 text-center">
						<div>
							<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">{countdown.days}</div>
							<div class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">{m.countdown_days()}</div>
						</div>
						<div>
							<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">{countdown.hours}</div>
							<div class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">{m.countdown_hours()}</div>
						</div>
						<div>
							<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">{countdown.minutes}</div>
							<div class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">{m.countdown_minutes()}</div>
						</div>
						<div>
							<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">{countdown.seconds}</div>
							<div class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">{m.countdown_seconds()}</div>
						</div>
					</div>
				</div>

				<!-- Assignment message -->
				<p class="mb-10 text-center text-sm text-slate-500 dark:text-slate-400">
					✨ {m.my_draw_will_happen()}
				</p>

				<!-- Primary action -->
				<div class="mb-8 flex justify-center">
					<a
						href={resolve(`/event/${status.event.id}`)}
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-pink-500 px-6 py-3 font-medium text-white shadow-lg transition-all hover:-translate-y-0.5 hover:shadow-xl"
					>
						<span>👥</span>
						{m.my_view_event_button()}
					</a>
				</div>

				<!-- Smart hint with copy option -->
				<div class="px-5 py-4">
					<p class="text-center text-sm text-slate-500 dark:text-slate-400">
						<span class="mr-1">📧</span>{m.my_email_hint()}
						<br />
						<span class="text-slate-400 dark:text-slate-500">{m.my_no_email_hint()}</span>
					</p>
					<div class="mt-3 flex justify-center">
						<Button
							variant="outline"
							size="sm"
							onclick={copyMyLink}
							class={linkCopied.active
								? 'border-emerald-500 bg-emerald-500/10 text-emerald-600'
								: ''}
						>
							{#if linkCopied.active}
								<CheckIcon class="h-4 w-4" />
								<span>{m.admin_copied()}</span>
							{:else}
								<CopyIcon class="h-4 w-4" />
								<span>{m.my_copy_link()}</span>
							{/if}
						</Button>
					</div>
				</div>
			</div>
		</div>
	{/if}
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
