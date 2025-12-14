<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { resolve } from '$app/paths';
	import { darkMode } from '$lib/stores/theme';
	import {
		PageLayout,
		Card,
		Button,
		Chip,
		ChevronLeftIcon,
		ChevronDownIcon,
		CheckIcon
	} from '$lib/components';
	import type { EventData, ParticipantData } from './+page';

	// Props from loader
	let { data } = $props();

	// Types
	interface Assignment {
		giver: string;
		receiver: string;
	}

	// Event data from loader (reactive to allow updates)
	let event = $state<EventData>(data.event);

	// Track which links have been copied (for feedback)
	let copiedStates = $state<Record<string, boolean>>({});

	// Draw state (initialized from backend data)
	let assignments = $state<Assignment[]>(event.assignments ?? []);
	let drawComplete = $state(event.drawComplete);
	let showDebug = $state(false);

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

	// Generate a valid derangement (no one gets themselves)
	function generateDerangement(participants: ParticipantData[]): Assignment[] {
		const names = participants.map((p) => p.name);
		const n = names.length;
		if (n < 2) return [];

		let receivers: string[];
		let isValid = false;

		// Keep shuffling until we get a valid derangement
		while (!isValid) {
			receivers = [...names];
			// Fisher-Yates shuffle
			for (let i = receivers.length - 1; i > 0; i--) {
				const j = Math.floor(Math.random() * (i + 1));
				[receivers[i], receivers[j]] = [receivers[j], receivers[i]];
			}
			// Check if it's a valid derangement (no one gets themselves)
			isValid = names.every((name, i) => name !== receivers[i]);
		}

		return names.map((giver, i) => ({
			giver,
			receiver: receivers![i]
		}));
	}

	// Handle draw button click
	async function handleDraw() {
		if (event.participants.length < 2) {
			alert('Need at least 2 participants for a draw!');
			return;
		}

		// For now, generate locally (demo mode)
		// TODO: Replace with actual API call when backend is ready
		assignments = generateDerangement(event.participants);
		drawComplete = true;
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
</script>

<svelte:head>
	<title>{event.name} - {m.app_name()}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<!-- Page Title -->
	<section class="py-6 sm:py-8">
		<div class="mx-auto max-w-3xl">
			<a
				href={resolve('/')}
				class="mb-4 inline-flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-rose-500 {$darkMode
					? 'text-slate-400'
					: 'text-slate-500'}"
			>
				<ChevronLeftIcon />
				{m.admin_back_home()}
			</a>
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
		<!-- Event Summary Card -->
		<Card class="p-6 sm:p-6">
			<h2
				class="mb-5 flex items-center gap-2 text-lg font-semibold {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				<span
					class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 text-sm text-white shadow-md shadow-emerald-400/35"
				>
					📋
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
							{event.maxAmount}
							{m.currency_suffix()}
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
			</div>
		</Card>

		<!-- Share Links Card -->
		<Card class="p-6 sm:p-6">
			<h2
				class="mb-2 flex items-center gap-2 text-lg font-semibold {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				<span
					class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-sm text-white shadow-md shadow-orange-400/35"
				>
					🔗
				</span>
				{m.admin_share_links()}
			</h2>
			<p class="mb-5 text-sm {$darkMode ? 'text-slate-400' : 'text-slate-500'}">
				{m.admin_share_links_desc()}
			</p>

			<div class="space-y-3">
				{#each event.participants as participant (participant.token)}
					<div
						class="flex items-center gap-3 rounded-xl p-3 transition-colors {$darkMode
							? 'bg-slate-700/50'
							: 'bg-slate-50'}"
					>
						<div
							class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full font-medium {$darkMode
								? 'bg-slate-600 text-slate-200'
								: 'bg-white text-slate-600 shadow-sm'}"
						>
							{participant.name.charAt(0).toUpperCase()}
						</div>
						<div class="min-w-0 flex-1">
							<div class="font-medium {$darkMode ? 'text-white' : 'text-slate-800'}">
								{participant.name}
							</div>
							<div class="truncate text-xs {$darkMode ? 'text-slate-500' : 'text-slate-400'}">
								/join/{participant.token}
							</div>
						</div>
						<button
							type="button"
							onclick={() => copyLink(participant)}
							class="shrink-0 rounded-lg px-3 py-2 text-sm font-medium transition-all {copiedStates[
								participant.token
							]
								? 'bg-emerald-500 text-white'
								: $darkMode
									? 'bg-slate-600 text-slate-200 hover:bg-slate-500'
									: 'bg-white text-slate-600 shadow-sm hover:bg-slate-100'}"
						>
							{#if copiedStates[participant.token]}
								<span class="flex items-center gap-1">
									<CheckIcon />
									{m.admin_copied()}
								</span>
							{:else}
								{m.admin_copy_link()}
							{/if}
						</button>
					</div>
				{/each}
			</div>
		</Card>

		<!-- Draw Assignments Card -->
		<Card class="p-6 sm:p-6">
			<h2
				class="mb-2 flex items-center gap-2 text-lg font-semibold {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				<span
					class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-rose-400 to-rose-500 text-sm text-white shadow-md shadow-rose-400/35"
				>
					🎲
				</span>
				{m.admin_draw_title()}
			</h2>
			<p class="mb-5 text-sm {$darkMode ? 'text-slate-400' : 'text-slate-500'}">
				{m.admin_draw_desc()}
			</p>

			{#if !drawComplete}
				<Button onclick={handleDraw}>{m.admin_draw_button()}</Button>
			{:else}
				<!-- Success Banner -->
				<div
					class="mb-4 rounded-xl border p-4 {$darkMode
						? 'border-emerald-500/30 bg-emerald-500/10'
						: 'border-emerald-200 bg-emerald-50'}"
				>
					<div class="flex items-start gap-3">
						<span
							class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white"
						>
							<CheckIcon class="h-5 w-5" />
						</span>
						<div>
							<div class="font-semibold {$darkMode ? 'text-emerald-400' : 'text-emerald-700'}">
								{m.admin_draw_already_done()}
							</div>
							<p class="mt-1 text-sm {$darkMode ? 'text-emerald-300/70' : 'text-emerald-600'}">
								{m.admin_draw_success()}
							</p>
						</div>
					</div>
				</div>

				<!-- Debug Section -->
				<div class="rounded-xl border {$darkMode ? 'border-slate-600' : 'border-slate-200'}">
					<button
						type="button"
						onclick={() => (showDebug = !showDebug)}
						class="flex w-full items-center justify-between rounded-xl px-4 py-3 text-left text-sm font-medium transition-colors {$darkMode
							? 'text-slate-400 hover:bg-slate-700/50'
							: 'text-slate-500 hover:bg-slate-50'}"
					>
						<span>{m.admin_debug_title()}</span>
						<ChevronDownIcon class="h-5 w-5 transition-transform {showDebug ? 'rotate-180' : ''}" />
					</button>
					{#if showDebug}
						<div class="border-t px-4 py-3 {$darkMode ? 'border-slate-600' : 'border-slate-200'}">
							<pre
								class="overflow-x-auto rounded-lg p-3 text-xs {$darkMode
									? 'bg-slate-900 text-slate-300'
									: 'bg-slate-100 text-slate-700'}">{JSON.stringify(assignments, null, 2)}</pre>
						</div>
					{/if}
				</div>
			{/if}
		</Card>
	</div>
</PageLayout>
