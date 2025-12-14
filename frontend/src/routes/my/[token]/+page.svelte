<script lang="ts">
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
	const token: string = data.token;

	// Countdown state
	let countdown = $state({ days: 0, hours: 0, minutes: 0, seconds: 0 });
	let countdownInterval: ReturnType<typeof setInterval> | null = null;

	// Feedback states
	const linkCopied = createFeedbackState(2500);

	// Derived states
	let deadlinePassed = $derived(new Date(status.event.registration_deadline) <= new Date());
	let myLink = $derived(typeof window !== 'undefined' ? window.location.href : '');

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
				// Reload to get assignment
				window.location.reload();
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
</script>

<svelte:head>
	<title>{m.my_status_title()} - {status.event.name}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<section class="py-6 sm:py-8">
		<div class="mx-auto max-w-xl">
			<!-- Header -->
			<div class="mb-6 text-center">
				<div
					class="mb-3 inline-block rounded-full bg-gradient-to-r from-orange-500 to-pink-500 px-4 py-1.5 text-sm font-medium text-white"
				>
					🎄 {status.event.name}
				</div>
				<h1 class="mb-2 text-2xl font-bold text-slate-800 sm:text-3xl dark:text-white">
					{m.my_greeting({ name: status.participant_name })}
				</h1>
			</div>

			{#if status.assignment}
				<!-- Assignment Revealed -->
				<Card class="mb-6 p-8 text-center">
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
							<div class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-300">
								<span>📅</span>
								<span>
									{m.join_event_date()}:
									<strong>{formatDateLong(status.event.date, getLocale())}</strong>
								</span>
							</div>
						{/if}
						{#if status.event.max_amount}
							<div class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-300">
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
								{#each status.assignment.receiver_wishlist.split(',').map((w) => w.trim()) as wish}
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
					class="mb-6 flex items-center justify-center gap-2 text-center text-sm text-slate-500 dark:text-slate-400"
				>
					<span>🤫</span>
					{m.join_keep_secret()}
				</p>

				<!-- Link to event page -->
				<div class="text-center">
					<a
						href="/event/{status.event.id}"
						class="inline-flex items-center gap-2 text-sm text-slate-500 transition-colors hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
					>
						<span>👥</span>
						{m.my_view_event_button()}
					</a>
				</div>
			{:else}
				<!-- Waiting for Draw -->
				<Card class="mb-6 p-6">
					<div class="mb-4 flex items-center gap-2 rounded-lg bg-amber-50 p-3 dark:bg-amber-500/10">
						<span class="text-xl">⏳</span>
						<span class="text-sm font-medium text-amber-700 dark:text-amber-400">
							{m.my_waiting_for_draw()}
						</span>
					</div>

					<!-- Countdown Timer -->
					<div class="rounded-xl bg-gradient-to-br from-orange-500 to-pink-500 p-6 text-white">
						<h3 class="mb-4 text-center text-sm font-medium uppercase tracking-wide opacity-90">
							{m.countdown_title()}
						</h3>
						<div class="grid grid-cols-4 gap-2 text-center">
							<div>
								<div class="text-3xl font-bold sm:text-4xl">{countdown.days}</div>
								<div class="text-xs uppercase opacity-75">{m.countdown_days()}</div>
							</div>
							<div>
								<div class="text-3xl font-bold sm:text-4xl">{countdown.hours}</div>
								<div class="text-xs uppercase opacity-75">{m.countdown_hours()}</div>
							</div>
							<div>
								<div class="text-3xl font-bold sm:text-4xl">{countdown.minutes}</div>
								<div class="text-xs uppercase opacity-75">{m.countdown_minutes()}</div>
							</div>
							<div>
								<div class="text-3xl font-bold sm:text-4xl">{countdown.seconds}</div>
								<div class="text-xs uppercase opacity-75">{m.countdown_seconds()}</div>
							</div>
						</div>
						<p class="mt-4 text-center text-sm opacity-90">
							{m.my_draw_will_happen()}
						</p>
					</div>
				</Card>

				<!-- Save this link notice -->
				<Card class="p-4">
					<div class="flex items-start gap-3">
						<span class="text-2xl">🔗</span>
						<div class="flex-1">
							<p class="mb-2 font-medium text-slate-800 dark:text-white">
								{m.my_save_link_title()}
							</p>
							<p class="mb-3 text-sm text-slate-500 dark:text-slate-400">
								{m.my_save_link_desc()}
							</p>
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
				</Card>

				<!-- Link to event page -->
				<Card class="p-4">
					<div class="flex items-start gap-3">
						<span class="text-2xl">👥</span>
						<div class="flex-1">
							<p class="mb-2 font-medium text-slate-800 dark:text-white">
								{m.my_view_event_title()}
							</p>
							<p class="mb-3 text-sm text-slate-500 dark:text-slate-400">
								{m.my_view_event_desc()}
							</p>
							<a
								href="/event/{status.event.id}"
								class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
							>
								{m.my_view_event_button()}
							</a>
						</div>
					</div>
				</Card>
			{/if}
		</div>
	</section>
</PageLayout>
