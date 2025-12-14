<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { darkMode } from '$lib/stores/theme';
	import { PageLayout, Card, Chip, CheckIcon, CopyIcon, MailIcon } from '$lib/components';
	import type { EventData, ParticipantData } from './+page';

	// Props from loader
	let { data } = $props();

	// Event data from loader (reactive to allow updates)
	let event = $state<EventData>(data.event);

	// Track which links have been copied (for feedback)
	let copiedStates = $state<Record<string, boolean>>({});
	let allCopied = $state(false);

	// Email drafts / saving state
	let emailDrafts = $state<Record<string, string>>({});
	let emailSaving = $state<Record<string, boolean>>({});
	let emailSaved = $state<Record<string, boolean>>({});
	let expandedEmails = $state<Record<string, boolean>>({});

	// Send emails state
	let sendingEmails = $state(false);
	let emailsSent = $state(false);
	let emailsSentCount = $state(0);

	for (const p of data.event.participants) {
		if (emailDrafts[p.token] === undefined) emailDrafts[p.token] = p.email ?? '';
	}

	// Count participants with emails
	let participantsWithEmail = $derived(event.participants.filter((p) => p.email).length);

	// Copy link to clipboard
	async function copyLink(participant: ParticipantData) {
		const link = `${window.location.origin}/join/${participant.token}`;
		try {
			await navigator.clipboard.writeText(link);
			copiedStates[participant.token] = true;
			setTimeout(() => {
				copiedStates[participant.token] = false;
			}, 2000);
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	// Copy all links at once
	async function copyAllLinks() {
		const links = event.participants
			.map((p) => `${p.name}: ${window.location.origin}/join/${p.token}`)
			.join('\n');
		try {
			await navigator.clipboard.writeText(links);
			allCopied = true;
			setTimeout(() => {
				allCopied = false;
			}, 2500);
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	// Send emails to all participants with email addresses
	async function sendEmails() {
		sendingEmails = true;
		emailsSent = false;
		try {
			const response = await fetch(`/api/event/${event.id}/send-emails`, {
				method: 'POST'
			});
			if (!response.ok) {
				console.error('Failed to send emails', await response.text());
				alert('Failed to send emails.');
				return;
			}
			const result = (await response.json()) as { sent_count: number; skipped_count: number };
			emailsSentCount = result.sent_count;
			emailsSent = true;
			setTimeout(() => {
				emailsSent = false;
			}, 3000);
		} finally {
			sendingEmails = false;
		}
	}

	async function saveEmail(participant: ParticipantData) {
		const id = participant.token;
		emailSaving[id] = true;
		emailSaved[id] = false;
		try {
			const email = (emailDrafts[id] ?? '').trim();
			const response = await fetch(`/api/participant/${id}`, {
				method: 'PATCH',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ email: email.length ? email : null })
			});
			if (!response.ok) {
				console.error('Failed to update participant', await response.text());
				alert('Failed to update participant email.');
				return;
			}

			const updated = (await response.json()) as { id: number; email: string | null; name: string };
			const next = [...event.participants];
			const idx = next.findIndex((p) => p.token === String(updated.id));
			if (idx !== -1) next[idx] = { ...next[idx], email: updated.email };
			event = { ...event, participants: next };
			emailSaved[id] = true;
			expandedEmails[id] = false; // Collapse after save
			setTimeout(() => (emailSaved[id] = false), 1500);
		} finally {
			emailSaving[id] = false;
		}
	}

	// Format date for display
	function formatDate(dateStr: string | null): string {
		if (!dateStr) return m.admin_date_not_set();
		const date = new Date(dateStr);
		return date.toLocaleDateString(getLocale() === 'pl' ? 'pl-PL' : 'en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function toggleEmailEdit(token: string) {
		expandedEmails[token] = !expandedEmails[token];
	}
</script>

<svelte:head>
	<title>{event.name} - {m.app_name()}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<!-- Page Title -->
	<section class="py-6 sm:py-8">
		<div class="mx-auto max-w-3xl">
			<h1
				class="text-2xl font-bold tracking-tight sm:text-3xl {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				{m.admin_event_dashboard()}
			</h1>
		</div>
	</section>

	<div class="mx-auto max-w-3xl space-y-6">
		<!-- STEP 1: Event Summary Card -->
		<Card class="p-6">
			<h2
				class="mb-5 flex items-center gap-3 text-lg font-semibold {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				<span
					class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 text-sm font-bold text-white shadow-md shadow-emerald-400/35"
				>
					1
				</span>
				{m.admin_event_summary()}
			</h2>

			<div class="space-y-4">
				<div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-4">
					<span class="text-2xl font-bold {$darkMode ? 'text-white' : 'text-slate-800'}">
						{event.name}
					</span>
				</div>

				<div class="grid gap-4 sm:grid-cols-2">
					<div class="rounded-xl p-4 {$darkMode ? 'bg-slate-700/50' : 'bg-slate-50'}">
						<span
							class="mb-1 block text-xs font-medium uppercase tracking-wide {$darkMode
								? 'text-slate-400'
								: 'text-slate-500'}"
						>
							{m.admin_max_amount_label()}
						</span>
						<span class="text-xl font-semibold {$darkMode ? 'text-white' : 'text-slate-800'}">
							{event.maxAmount ?? '—'}
							{event.maxAmount ? (event.currency ?? m.currency_suffix()) : ''}
						</span>
					</div>
					<div class="rounded-xl p-4 {$darkMode ? 'bg-slate-700/50' : 'bg-slate-50'}">
						<span
							class="mb-1 block text-xs font-medium uppercase tracking-wide {$darkMode
								? 'text-slate-400'
								: 'text-slate-500'}"
						>
							{m.admin_date_label()}
						</span>
						<span class="text-xl font-semibold {$darkMode ? 'text-white' : 'text-slate-800'}">
							{formatDate(event.date)}
						</span>
					</div>
				</div>

				<div>
					<span
						class="mb-2 block text-xs font-medium uppercase tracking-wide {$darkMode
							? 'text-slate-400'
							: 'text-slate-500'}"
					>
						{m.admin_participants_label()} ({event.participants.length})
					</span>
					<div class="flex flex-wrap gap-2">
						{#each event.participants as participant (participant.token)}
							<Chip>{participant.name}</Chip>
						{/each}
					</div>
				</div>

				<!-- Draw complete indicator -->
				<div
					class="flex items-center gap-2 rounded-lg p-3 {$darkMode
						? 'bg-emerald-500/10'
						: 'bg-emerald-50'}"
				>
					<span
						class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-white"
					>
						<CheckIcon class="h-4 w-4" />
					</span>
					<span class="text-sm font-medium {$darkMode ? 'text-emerald-400' : 'text-emerald-700'}">
						{m.admin_draw_auto_complete()}
					</span>
				</div>
			</div>
		</Card>

		<!-- STEP 2: Share Links Card -->
		<Card class="p-6">
			<h2
				class="mb-2 flex items-center gap-3 text-lg font-semibold {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				<span
					class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-sm font-bold text-white shadow-md shadow-orange-400/35"
				>
					2
				</span>
				{m.admin_share_links()}
			</h2>
			<p class="mb-5 text-sm {$darkMode ? 'text-slate-400' : 'text-slate-500'}">
				{m.admin_share_links_desc()}
			</p>

			<!-- Action buttons row -->
			<div class="mb-4 flex flex-col gap-3 sm:flex-row">
				<!-- Copy All Links Button -->
				<button
					type="button"
					onclick={copyAllLinks}
					class="flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed py-3 text-sm font-medium transition-all {allCopied
						? 'border-emerald-500 bg-emerald-500/10 text-emerald-600'
						: $darkMode
							? 'border-slate-600 text-slate-400 hover:border-orange-500 hover:bg-orange-500/5 hover:text-orange-400'
							: 'border-slate-300 text-slate-500 hover:border-orange-500 hover:bg-orange-500/5 hover:text-orange-500'}"
				>
					{#if allCopied}
						<CheckIcon class="h-4 w-4" />
						<span>{m.admin_all_copied()}</span>
					{:else}
						<CopyIcon class="h-4 w-4" />
						<span>{m.admin_copy_all_links()}</span>
					{/if}
				</button>

				<!-- Send All Emails Button -->
				<button
					type="button"
					onclick={sendEmails}
					disabled={sendingEmails || participantsWithEmail === 0}
					class="flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-xl py-3 text-sm font-medium transition-all disabled:cursor-not-allowed disabled:opacity-50 {emailsSent
						? 'bg-emerald-500 text-white'
						: $darkMode
							? 'bg-gradient-to-r from-orange-500 to-rose-500 text-white hover:from-orange-600 hover:to-rose-600'
							: 'bg-gradient-to-r from-orange-500 to-rose-500 text-white hover:from-orange-600 hover:to-rose-600'}"
				>
					{#if emailsSent}
						<CheckIcon class="h-4 w-4" />
						<span>{m.admin_emails_sent({ count: emailsSentCount })}</span>
					{:else if sendingEmails}
						<span>{m.admin_sending_emails()}</span>
					{:else}
						<MailIcon class="h-4 w-4" />
						<span>{m.admin_send_all_emails({ count: participantsWithEmail })}</span>
					{/if}
				</button>
			</div>

			<div class="space-y-2">
				{#each event.participants as participant (participant.token)}
					<div
						class="rounded-xl border transition-colors {$darkMode
							? 'border-slate-700 bg-slate-800/50'
							: 'border-slate-200 bg-white'}"
					>
						<!-- Main row: Avatar, Name, Actions -->
						<div class="flex items-center gap-3 p-3">
							<!-- Avatar -->
							<div
								class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold {$darkMode
									? 'bg-gradient-to-br from-slate-600 to-slate-700 text-slate-200'
									: 'bg-gradient-to-br from-slate-100 to-slate-200 text-slate-600'}"
							>
								{participant.name.charAt(0).toUpperCase()}
							</div>

							<!-- Name and email info -->
							<div class="min-w-0 flex-1">
								<div class="font-medium {$darkMode ? 'text-white' : 'text-slate-800'}">
									{participant.name}
								</div>
								{#if participant.email}
									<div
										class="flex items-center gap-1.5 text-xs {$darkMode
											? 'text-slate-400'
											: 'text-slate-500'}"
									>
										<MailIcon class="h-3 w-3" />
										<span class="truncate">{participant.email}</span>
									</div>
								{/if}
							</div>

							<!-- Actions -->
							<div class="flex shrink-0 items-center gap-2">
								<!-- Add/Edit Email Button -->
								<button
									type="button"
									onclick={() => toggleEmailEdit(participant.token)}
									class="flex cursor-pointer items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all {expandedEmails[
										participant.token
									]
										? $darkMode
											? 'bg-slate-700 text-orange-400'
											: 'bg-orange-50 text-orange-600'
										: $darkMode
											? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200'
											: 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'}"
								>
									<MailIcon class="h-3.5 w-3.5" />
									<span class="hidden sm:inline"
										>{participant.email ? m.admin_edit_email() : m.admin_add_email()}</span
									>
								</button>

								<!-- Copy Link Button -->
								<button
									type="button"
									onclick={() => copyLink(participant)}
									class="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all {copiedStates[
										participant.token
									]
										? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/25'
										: $darkMode
											? 'bg-slate-700 text-slate-200 hover:bg-slate-600'
											: 'bg-slate-100 text-slate-700 hover:bg-slate-200'}"
								>
									{#if copiedStates[participant.token]}
										<CheckIcon class="h-4 w-4" />
										<span class="hidden sm:inline">{m.admin_copied()}</span>
									{:else}
										<CopyIcon class="h-4 w-4" />
										<span class="hidden sm:inline">{m.admin_copy_link()}</span>
									{/if}
								</button>
							</div>
						</div>

						<!-- Expandable email edit section -->
						{#if expandedEmails[participant.token]}
							<div
								class="border-t px-3 py-3 {$darkMode ? 'border-slate-700/50' : 'border-slate-100'}"
							>
								<div class="flex flex-col gap-2 sm:flex-row sm:items-center">
									<div class="relative flex-1">
										<MailIcon
											class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 {$darkMode
												? 'text-slate-500'
												: 'text-slate-400'}"
										/>
										<input
											type="email"
											id={`email-${participant.token}`}
											bind:value={emailDrafts[participant.token]}
											placeholder={m.admin_email_placeholder()}
											class="w-full cursor-text rounded-lg border py-2 pl-10 pr-3 text-sm transition-colors focus:outline-none focus:ring-2 {$darkMode
												? 'border-slate-600 bg-slate-700/50 text-white placeholder-slate-500 focus:border-orange-500 focus:ring-orange-500/20'
												: 'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:border-orange-500 focus:ring-orange-500/20'}"
										/>
									</div>
									<button
										type="button"
										onclick={() => saveEmail(participant)}
										disabled={emailSaving[participant.token]}
										class="flex shrink-0 cursor-pointer items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all disabled:cursor-not-allowed disabled:opacity-60 {emailSaved[
											participant.token
										]
											? 'bg-emerald-500 text-white'
											: $darkMode
												? 'bg-orange-500 text-white hover:bg-orange-600'
												: 'bg-orange-500 text-white hover:bg-orange-600'}"
									>
										{#if emailSaved[participant.token]}
											<CheckIcon class="h-4 w-4" />
											<span>{m.admin_email_saved()}</span>
										{:else if emailSaving[participant.token]}
											<span>{m.admin_email_saving()}</span>
										{:else}
											<span>{m.admin_save_email()}</span>
										{/if}
									</button>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</Card>
	</div>
</PageLayout>
