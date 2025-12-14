<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { formatDateLong } from '$lib/utils/date';
	import { createFeedbackState } from '$lib/utils/feedback.svelte';
	import { fetchJson } from '$lib/api/client';
	import {
		PageLayout,
		Card,
		Chip,
		Button,
		CheckIcon,
		CopyIcon,
		MailIcon,
		ParticipantRow
	} from '$lib/components';
	import type { EventData, ParticipantData } from './+page';

	// Props from loader
	let { data } = $props();

	// Event data from loader (reactive to allow updates)
	let event = $state<EventData>(data.event);

	// Feedback states using the utility
	const allCopied = createFeedbackState(2500);
	const emailsSent = createFeedbackState(3000);

	// Send emails state
	let sendingEmails = $state(false);
	let emailsSentCount = $state(0);

	// Count participants with emails
	let participantsWithEmail = $derived(event.participants.filter((p) => p.email).length);

	// Copy all links at once
	async function copyAllLinks() {
		const links = event.participants
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
			alert('Failed to send emails.');
		} finally {
			sendingEmails = false;
		}
	}

	function handleParticipantUpdate(updated: ParticipantData) {
		const next = [...event.participants];
		const idx = next.findIndex((p) => p.id === updated.id);
		if (idx !== -1) {
			next[idx] = updated;
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

				<div>
					<span
						class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
					>
						{m.admin_participants_label()} ({event.participants.length})
					</span>
					<div class="flex flex-wrap gap-2">
						{#each event.participants as participant (participant.id)}
							<Chip>{participant.name}</Chip>
						{/each}
					</div>
				</div>

				<!-- Draw complete indicator -->
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
			</div>
		</Card>

		<!-- STEP 2: Share Links Card -->
		<Card class="p-6">
			<h2 class="mb-2 flex items-center gap-3 text-lg font-semibold text-slate-800 dark:text-white">
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
	</div>
</PageLayout>
