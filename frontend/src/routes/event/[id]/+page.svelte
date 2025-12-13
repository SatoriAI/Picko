<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale, setLocale, type Locale } from '$lib/paraglide/runtime';
	import type { EventData, ParticipantData } from './+page';

	// Props from loader
	let { data } = $props();

	// Types
	interface Assignment {
		giver: string;
		receiver: string;
	}

	// Dark mode state
	let darkMode = $state(false);

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

		// =================================================================
		// TODO: Replace with actual API call when backend is ready
		// Example:
		//
		// const response = await fetch(`/api/events/${event.id}/draw`, {
		//   method: 'POST'
		// });
		// if (!response.ok) {
		//   alert('Failed to generate draw');
		//   return;
		// }
		// const result = await response.json();
		// assignments = result.assignments;
		// drawComplete = true;
		// =================================================================

		// For now, generate locally (demo mode)
		assignments = generateDerangement(event.participants);
		drawComplete = true;
	}

	function toggleDarkMode() {
		darkMode = !darkMode;
	}

	function switchLocale(locale: Locale) {
		setLocale(locale);
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
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="min-h-screen font-[Outfit,system-ui,sans-serif] transition-colors duration-300 {darkMode ? 'bg-slate-900 text-slate-100' : 'bg-gradient-to-br from-amber-50 via-blue-50 to-orange-50 text-slate-800'}">
	<header class="sticky top-0 z-50 border-b px-4 py-4 backdrop-blur-md transition-colors duration-300 sm:px-6 {darkMode ? 'border-slate-700/50 bg-slate-900/85' : 'border-slate-900/5 bg-amber-50/85'}">
		<div class="mx-auto flex max-w-5xl items-center justify-between">
			<a href="/" class="flex items-center gap-2">
				<span class="text-2xl drop-shadow-sm">🎁</span>
				<span class="text-xl font-bold tracking-tight text-rose-500">{m.app_name()}</span>
			</a>
			<div class="flex items-center gap-3">
				<!-- Dark mode toggle -->
				<button
					type="button"
					onclick={toggleDarkMode}
					class="flex h-9 w-9 items-center justify-center rounded-lg transition-all {darkMode ? 'bg-slate-800 text-yellow-400 hover:bg-slate-700' : 'bg-white text-slate-600 shadow-sm hover:bg-slate-50'}"
					aria-label="Toggle dark mode"
				>
					{#if darkMode}
						<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
						</svg>
					{:else}
						<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
						</svg>
					{/if}
				</button>
				<!-- Language switcher -->
				<div class="flex items-center gap-1 rounded-xl p-1 shadow-sm transition-colors {darkMode ? 'bg-slate-800' : 'bg-white'}">
					<button
						type="button"
						class="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all {getLocale() === 'en' ? 'bg-rose-500 text-white shadow-sm' : darkMode ? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'}"
						onclick={() => switchLocale('en')}
					>
						<span>🇬🇧</span>
						<span class="hidden sm:inline">English</span>
					</button>
					<button
						type="button"
						class="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all {getLocale() === 'pl' ? 'bg-rose-500 text-white shadow-sm' : darkMode ? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'}"
						onclick={() => switchLocale('pl')}
					>
						<span>🇵🇱</span>
						<span class="hidden sm:inline">Polski</span>
					</button>
				</div>
			</div>
		</div>
	</header>

	<main class="px-4 pb-12 sm:px-6">
		<!-- Page Title -->
		<section class="py-6 sm:py-8">
			<div class="mx-auto max-w-3xl">
				<a
					href="/"
					class="mb-4 inline-flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-rose-500 {darkMode ? 'text-slate-400' : 'text-slate-500'}"
				>
					<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
					</svg>
					{m.admin_back_home()}
				</a>
				<h1 class="text-2xl font-bold tracking-tight sm:text-3xl {darkMode ? 'text-white' : 'text-slate-800'}">
					{m.admin_event_dashboard()}
				</h1>
			</div>
		</section>

		<div class="mx-auto max-w-3xl space-y-6">
			<!-- Event Summary Card -->
			<section class="rounded-2xl border p-6 shadow-lg transition-colors {darkMode ? 'border-slate-700/50 bg-slate-800/80 shadow-slate-900/50' : 'border-slate-900/5 bg-white shadow-slate-900/5'}">
				<h2 class="mb-5 flex items-center gap-2 text-lg font-semibold {darkMode ? 'text-white' : 'text-slate-800'}">
					<span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 text-sm text-white shadow-md shadow-emerald-400/35">
						📋
					</span>
					{m.admin_event_summary()}
				</h2>
				
				<div class="space-y-4">
					<div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-4">
						<span class="text-2xl font-bold {darkMode ? 'text-white' : 'text-slate-800'}">{event.name}</span>
					</div>
					
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="rounded-xl p-4 {darkMode ? 'bg-slate-700/50' : 'bg-slate-50'}">
							<span class="mb-1 block text-xs font-medium uppercase tracking-wide {darkMode ? 'text-slate-400' : 'text-slate-500'}">
								{m.admin_max_amount_label()}
							</span>
							<span class="text-xl font-semibold {darkMode ? 'text-white' : 'text-slate-800'}">
								{event.maxAmount} {m.currency_suffix()}
							</span>
						</div>
						<div class="rounded-xl p-4 {darkMode ? 'bg-slate-700/50' : 'bg-slate-50'}">
							<span class="mb-1 block text-xs font-medium uppercase tracking-wide {darkMode ? 'text-slate-400' : 'text-slate-500'}">
								{m.admin_date_label()}
							</span>
							<span class="text-xl font-semibold {darkMode ? 'text-white' : 'text-slate-800'}">
								{formatDate(event.date)}
							</span>
						</div>
					</div>

					<div>
						<span class="mb-2 block text-xs font-medium uppercase tracking-wide {darkMode ? 'text-slate-400' : 'text-slate-500'}">
							{m.admin_participants_label()} ({event.participants.length})
						</span>
						<div class="flex flex-wrap gap-2">
							{#each event.participants as participant}
								<span class="participant-chip {darkMode ? 'participant-chip--dark' : ''}">
									{participant.name}
								</span>
							{/each}
						</div>
					</div>
				</div>
			</section>

			<!-- Share Links Card -->
			<section class="rounded-2xl border p-6 shadow-lg transition-colors {darkMode ? 'border-slate-700/50 bg-slate-800/80 shadow-slate-900/50' : 'border-slate-900/5 bg-white shadow-slate-900/5'}">
				<h2 class="mb-2 flex items-center gap-2 text-lg font-semibold {darkMode ? 'text-white' : 'text-slate-800'}">
					<span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-sm text-white shadow-md shadow-orange-400/35">
						🔗
					</span>
					{m.admin_share_links()}
				</h2>
				<p class="mb-5 text-sm {darkMode ? 'text-slate-400' : 'text-slate-500'}">
					{m.admin_share_links_desc()}
				</p>

				<div class="space-y-3">
					{#each event.participants as participant}
						<div class="flex items-center gap-3 rounded-xl p-3 transition-colors {darkMode ? 'bg-slate-700/50' : 'bg-slate-50'}">
							<div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full font-medium {darkMode ? 'bg-slate-600 text-slate-200' : 'bg-white text-slate-600 shadow-sm'}">
								{participant.name.charAt(0).toUpperCase()}
							</div>
							<div class="min-w-0 flex-1">
								<div class="font-medium {darkMode ? 'text-white' : 'text-slate-800'}">{participant.name}</div>
								<div class="truncate text-xs {darkMode ? 'text-slate-500' : 'text-slate-400'}">
									/join/{participant.token}
								</div>
							</div>
							<button
								type="button"
								onclick={() => copyLink(participant)}
								class="shrink-0 rounded-lg px-3 py-2 text-sm font-medium transition-all {copiedStates[participant.token] 
									? 'bg-emerald-500 text-white' 
									: darkMode 
										? 'bg-slate-600 text-slate-200 hover:bg-slate-500' 
										: 'bg-white text-slate-600 shadow-sm hover:bg-slate-100'}"
							>
								{#if copiedStates[participant.token]}
									<span class="flex items-center gap-1">
										<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
											<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
										</svg>
										{m.admin_copied()}
									</span>
								{:else}
									{m.admin_copy_link()}
								{/if}
							</button>
						</div>
					{/each}
				</div>
			</section>

			<!-- Draw Assignments Card -->
			<section class="rounded-2xl border p-6 shadow-lg transition-colors {darkMode ? 'border-slate-700/50 bg-slate-800/80 shadow-slate-900/50' : 'border-slate-900/5 bg-white shadow-slate-900/5'}">
				<h2 class="mb-2 flex items-center gap-2 text-lg font-semibold {darkMode ? 'text-white' : 'text-slate-800'}">
					<span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-rose-400 to-rose-500 text-sm text-white shadow-md shadow-rose-400/35">
						🎲
					</span>
					{m.admin_draw_title()}
				</h2>
				<p class="mb-5 text-sm {darkMode ? 'text-slate-400' : 'text-slate-500'}">
					{m.admin_draw_desc()}
				</p>

				{#if !drawComplete}
					<button
						type="button"
						onclick={handleDraw}
						class="w-full cursor-pointer rounded-xl bg-gradient-to-r from-orange-400 to-rose-500 px-6 py-3.5 text-base font-semibold text-white shadow-md shadow-rose-500/30 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-rose-500/40 active:translate-y-0 active:shadow-md"
					>
						{m.admin_draw_button()}
					</button>
				{:else}
					<!-- Success Banner -->
					<div class="mb-4 rounded-xl border p-4 {darkMode ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-emerald-200 bg-emerald-50'}">
						<div class="flex items-start gap-3">
							<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white">
								<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
								</svg>
							</span>
							<div>
								<div class="font-semibold {darkMode ? 'text-emerald-400' : 'text-emerald-700'}">
									{m.admin_draw_already_done()}
								</div>
								<p class="mt-1 text-sm {darkMode ? 'text-emerald-300/70' : 'text-emerald-600'}">
									{m.admin_draw_success()}
								</p>
							</div>
						</div>
					</div>

					<!-- Debug Section -->
					<div class="rounded-xl border {darkMode ? 'border-slate-600' : 'border-slate-200'}">
						<button
							type="button"
							onclick={() => showDebug = !showDebug}
							class="flex w-full items-center justify-between rounded-xl px-4 py-3 text-left text-sm font-medium transition-colors {darkMode ? 'text-slate-400 hover:bg-slate-700/50' : 'text-slate-500 hover:bg-slate-50'}"
						>
							<span>{m.admin_debug_title()}</span>
							<svg 
								class="h-5 w-5 transition-transform {showDebug ? 'rotate-180' : ''}" 
								fill="none" 
								viewBox="0 0 24 24" 
								stroke="currentColor" 
								stroke-width="2"
							>
								<path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
							</svg>
						</button>
						{#if showDebug}
							<div class="border-t px-4 py-3 {darkMode ? 'border-slate-600' : 'border-slate-200'}">
								<pre class="overflow-x-auto rounded-lg p-3 text-xs {darkMode ? 'bg-slate-900 text-slate-300' : 'bg-slate-100 text-slate-700'}">{JSON.stringify(assignments, null, 2)}</pre>
							</div>
						{/if}
					</div>
				{/if}
			</section>
		</div>
	</main>

	<footer class="border-t px-4 py-8 backdrop-blur-sm transition-colors sm:px-6 {darkMode ? 'border-slate-700/50 bg-slate-800/50' : 'border-slate-900/5 bg-white/50'}">
		<div class="mx-auto flex max-w-5xl flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left">
			<p class="text-sm {darkMode ? 'text-slate-500' : 'text-slate-500'}">
				© {new Date().getFullYear()} Created by Dawid Hanrahan
			</p>
			<div class="flex items-center gap-5">
				<a
					href="https://dawidhanrahan.com"
					target="_blank"
					rel="noopener noreferrer"
					class="text-sm font-medium transition-colors hover:text-rose-500 {darkMode ? 'text-slate-400' : 'text-slate-500'}"
				>
					dawidhanrahan.com
				</a>
				<a
					href="https://github.com/dawidhanrahan"
					target="_blank"
					rel="noopener noreferrer"
					class="transition-colors hover:text-rose-500 {darkMode ? 'text-slate-500' : 'text-slate-400'}"
					aria-label="GitHub"
				>
					<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
						<path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
					</svg>
				</a>
			</div>
		</div>
	</footer>
</div>

<style>
	.participant-chip {
		display: inline-flex;
		align-items: center;
		padding: 0.5rem 0.875rem;
		font-size: 0.875rem;
		font-weight: 500;
		line-height: 1;
		color: #475569;
		background-color: #f1f5f9;
		border: 1px solid #e2e8f0;
		border-radius: 9999px;
	}

	.participant-chip--dark {
		color: #cbd5e1;
		background-color: #334155;
		border-color: #475569;
	}
</style>
