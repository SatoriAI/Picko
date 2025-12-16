<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { formatDateLong } from '$lib/utils/date';
	import { createFeedbackState } from '$lib/utils/feedback.svelte';
	import { fetchJson } from '$lib/api/client';
	import { onMount, onDestroy } from 'svelte';
	import {
		PageLayout,
		Card,
		Chip,
		Button,
		Input,
		CheckIcon,
		CopyIcon,
		MailIcon,
		ParticipantRow
	} from '$lib/components';
	import type { EventData } from './+page';

	// Props from loader
	let { data } = $props();

	// Event data from loader (reactive to allow updates)
	let event = $state<EventData>(data.event);

	// Feedback states using the utility
	const linkCopied = createFeedbackState(2500);
	const allCopied = createFeedbackState(2500);
	const emailsSent = createFeedbackState(3000);

	// Send emails state
	let sendingEmails = $state(false);
	let emailsSentCount = $state(0);

	// Countdown state
	let countdown = $state({ days: 0, hours: 0, minutes: 0, seconds: 0 });
	let countdownInterval: ReturnType<typeof setInterval> | null = null;

	// Derived states
	let deadlinePassed = $derived(new Date(event.registrationDeadline) <= new Date());
	let participantsWithEmail = $derived(event.participants.filter((p) => p.email).length);
	let registrationUrl = $derived(
		typeof window !== 'undefined'
			? `${window.location.origin}/register/${event.registrationToken}`
			: `/register/${event.registrationToken}`
	);

	// Calculate countdown
	function updateCountdown() {
		const now = new Date().getTime();
		const deadline = new Date(event.registrationDeadline).getTime();
		const diff = deadline - now;

		if (diff <= 0) {
			countdown = { days: 0, hours: 0, minutes: 0, seconds: 0 };
			if (countdownInterval) {
				clearInterval(countdownInterval);
				countdownInterval = null;
				// Reload to trigger draw
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
		if (!deadlinePassed) {
			countdownInterval = setInterval(updateCountdown, 1000);
		}
	});

	onDestroy(() => {
		if (countdownInterval) {
			clearInterval(countdownInterval);
		}
	});

	// Copy registration link
	async function copyRegistrationLink() {
		try {
			await navigator.clipboard.writeText(registrationUrl);
			linkCopied.trigger();
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	// Copy all reveal links at once
	async function copyAllLinks() {
		const links = event.participants
			.filter((p) => p.shareToken)
			.map((p) => `${p.name}: ${window.location.origin}/join/${p.shareToken}`)
			.join('\n');
		try {
			await navigator.clipboard.writeText(links);
			allCopied.trigger();
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	// Send emails to all participants with email addresses
	async function sendEmails() {
		sendingEmails = true;
		emailsSent.reset();
		try {
			const result = await fetchJson<{ sent_count: number; skipped_count: number }>(
				`/api/event/${event.id}/send-emails`,
				{
					method: 'POST'
				}
			);

			emailsSentCount = result.sent_count;
			emailsSent.trigger();
		} catch (err) {
			console.error('Failed to send emails', err);
			alert(m.email_send_failed());
		} finally {
			sendingEmails = false;
		}
	}

	function handleParticipantUpdate(updated: {
		id: number;
		name: string;
		email?: string | null;
		shareToken?: string | null;
	}) {
		const next = [...event.participants];
		const idx = next.findIndex((p) => p.id === updated.id);
		if (idx !== -1) {
			next[idx] = { ...next[idx], ...updated };
			event = { ...event, participants: next };
		}
	}
</script>

<svelte:head>
	<title>{event.name} - {m.app_name()}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<!-- Page Title -->
	<section class="py-6 sm:py-8">
		<div class="mx-auto max-w-3xl">
			<h1 class="text-2xl font-bold tracking-tight text-slate-800 sm:text-3xl dark:text-white">
				{m.admin_event_dashboard()}
			</h1>
		</div>
	</section>

	<div class="mx-auto max-w-3xl space-y-6">
		<!-- STEP 1: Event Summary Card -->
		<Card class="p-6">
			<h2 class="mb-5 flex items-center gap-3 text-lg font-semibold text-slate-800 dark:text-white">
				<span
					class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 text-sm font-bold text-white shadow-md shadow-emerald-400/35"
				>
					1
				</span>
				{m.admin_event_summary()}
			</h2>

			<div class="space-y-4">
				<div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-4">
					<span class="text-2xl font-bold text-slate-800 dark:text-white">
						{event.name}
					</span>
				</div>

				<div class="grid gap-4 sm:grid-cols-2">
					<div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-700/50">
						<span
							class="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
						>
							{m.admin_max_amount_label()}
						</span>
						<span class="text-xl font-semibold text-slate-800 dark:text-white">
							{event.maxAmount ?? '—'}
							{event.maxAmount ? (event.currency ?? m.currency_suffix()) : ''}
						</span>
					</div>
					<div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-700/50">
						<span
							class="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
						>
							{m.admin_date_label()}
						</span>
						<span class="text-xl font-semibold text-slate-800 dark:text-white">
							{formatDateLong(event.date, getLocale(), { empty: m.admin_date_not_set() })}
						</span>
					</div>
				</div>

				<!-- Status indicator -->
				{#if event.isDrawComplete}
					<div class="flex items-center gap-2 rounded-lg bg-emerald-50 p-3 dark:bg-emerald-500/10">
						<span
							class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-white"
						>
							<CheckIcon class="h-4 w-4" />
						</span>
						<span class="text-sm font-medium text-emerald-700 dark:text-emerald-400">
							{m.admin_draw_auto_complete()}
						</span>
					</div>
				{/if}
			</div>
		</Card>

		{#if !deadlinePassed}
			<!-- STEP 2: Share Registration Link (before deadline) -->
			<Card class="p-6">
				<h2
					class="mb-2 flex items-center gap-3 text-lg font-semibold text-slate-800 dark:text-white"
				>
					<span
						class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-sm font-bold text-white shadow-md shadow-orange-400/35"
					>
						2
					</span>
					{m.share_link_title()}
				</h2>
				<p class="mb-5 text-sm text-slate-500 dark:text-slate-400">
					{m.share_link_desc()}
				</p>

				<!-- Registration Link -->
				<div class="mb-6 flex gap-2">
					<Input
						id="registrationUrl"
						value={registrationUrl}
						readonly
						class="flex-1 font-mono text-sm"
					/>
					<Button
						variant="outline"
						onclick={copyRegistrationLink}
						class={linkCopied.active ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600' : ''}
					>
						{#if linkCopied.active}
							<CheckIcon class="h-4 w-4" />
						{:else}
							<CopyIcon class="h-4 w-4" />
						{/if}
						<span>{linkCopied.active ? m.admin_copied() : m.admin_copy_link()}</span>
					</Button>
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
						{m.draw_at_deadline()}
					</p>
				</div>
			</Card>

			<!-- Registered Participants with Wishlists -->
			{#if event.participants.length > 0}
				<Card class="p-6">
					<h2
						class="mb-4 flex items-center gap-3 text-lg font-semibold text-slate-800 dark:text-white"
					>
						<span
							class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-rose-400 to-rose-500 text-sm font-bold text-white shadow-md shadow-rose-400/35"
						>
							3
						</span>
						{m.registered_participants()}
					</h2>

					<div class="space-y-3">
						{#each event.participants as participant (participant.id)}
							<div class="rounded-lg bg-slate-50 p-4 dark:bg-slate-700/50">
								<div class="flex items-center justify-between">
									<div>
										<span class="font-medium text-slate-800 dark:text-white">
											{participant.name}
										</span>
										{#if participant.email}
											<span class="ml-2 text-sm text-slate-500 dark:text-slate-400">
												({participant.email})
											</span>
										{/if}
									</div>
									<Chip>
										{participant.language === 'pl' ? '🇵🇱' : '🇬🇧'}
									</Chip>
								</div>
								{#if participant.wishlist}
									<div class="mt-2">
										<span
											class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
										>
											{m.wishlist_label()}:
										</span>
										<div class="mt-1 flex flex-wrap gap-1">
											{#each participant.wishlist.split(',').map((w) => w.trim()) as wish (wish)}
												{#if wish}
													<span
														class="rounded-full bg-white px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-600 dark:text-slate-300"
													>
														🎁 {wish}
													</span>
												{/if}
											{/each}
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				</Card>
			{/if}
		{:else if event.isDrawComplete}
			<!-- STEP 2: Share Reveal Links (after deadline + draw complete) -->
			<Card class="p-6">
				<h2
					class="mb-2 flex items-center gap-3 text-lg font-semibold text-slate-800 dark:text-white"
				>
					<span
						class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-sm font-bold text-white shadow-md shadow-orange-400/35"
					>
						2
					</span>
					{m.admin_share_links()}
				</h2>
				<p class="mb-5 text-sm text-slate-500 dark:text-slate-400">
					{m.admin_share_links_desc()}
				</p>

				<!-- Action buttons row -->
				<div class="mb-4 flex flex-col gap-3 sm:flex-row">
					<!-- Copy All Links Button -->
					<Button
						variant="outline"
						size="md"
						onclick={copyAllLinks}
						class="flex-1 py-3 {allCopied.active
							? 'border-emerald-500 bg-emerald-500/10 text-emerald-600 hover:border-emerald-500 hover:bg-emerald-500/10 hover:text-emerald-600'
							: ''}"
					>
						{#if allCopied.active}
							<CheckIcon class="h-4 w-4" />
							<span>{m.admin_all_copied()}</span>
						{:else}
							<CopyIcon class="h-4 w-4" />
							<span>{m.admin_copy_all_links()}</span>
						{/if}
					</Button>

					<!-- Send All Emails Button -->
					<Button
						size="md"
						onclick={sendEmails}
						disabled={sendingEmails || participantsWithEmail === 0}
						class="flex-1 py-3 {emailsSent.active
							? 'bg-emerald-500 from-emerald-500 to-emerald-500 shadow-emerald-500/30'
							: ''}"
					>
						{#if emailsSent.active}
							<CheckIcon class="h-4 w-4" />
							<span>{m.admin_emails_sent({ count: emailsSentCount })}</span>
						{:else if sendingEmails}
							<span>{m.admin_sending_emails()}</span>
						{:else}
							<MailIcon class="h-4 w-4" />
							<span>{m.admin_send_all_emails({ count: participantsWithEmail })}</span>
						{/if}
					</Button>
				</div>

				<div class="space-y-2">
					{#each event.participants as participant (participant.id)}
						<ParticipantRow {participant} onUpdate={handleParticipantUpdate} />
					{/each}
				</div>
			</Card>
		{:else}
			<!-- Waiting for draw (deadline passed but not enough participants) -->
			<Card class="p-6 text-center">
				<div class="mb-4 text-5xl">😢</div>
				<h2 class="mb-2 text-xl font-semibold text-slate-800 dark:text-white">
					{m.not_enough_participants_title()}
				</h2>
				<p class="text-slate-500 dark:text-slate-400">
					{m.not_enough_participants_desc()}
				</p>
			</Card>
		{/if}
	</div>
</PageLayout>
