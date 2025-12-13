<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale, setLocale, type Locale } from '$lib/paraglide/runtime';

	let darkMode = $state(false);
	let eventName = $state('');
	let maxAmount = $state('');
	let eventDate = $state('');
	let participantsInput = $state('');

	// Derived array of parsed participant names
	let participants = $derived(
		participantsInput
			.split(',')
			.map((p) => p.trim())
			.filter((p) => p.length > 0)
	);

	function handleSubmit() {
		if (!eventName.trim() || !maxAmount.trim() || participants.length === 0) {
			alert(m.validation_error());
			return;
		}

		console.log({
			eventName: eventName.trim(),
			maxAmount: Number(maxAmount),
			date: eventDate || null,
			participants
		});

		alert(m.success_alert());
	}

	function handleDemo() {
		eventName = m.demo_event_name();
		maxAmount = '150';
		eventDate = '2025-12-24';
		participantsInput = m.demo_participants();
	}

	function toggleDarkMode() {
		darkMode = !darkMode;
	}

	function switchLocale(locale: Locale) {
		// Use setLocale to update the cookie and reload the page
		// This ensures the server-side rendering uses the correct locale
		setLocale(locale);
	}
</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div
	class="min-h-screen font-[Outfit,system-ui,sans-serif] transition-colors duration-300 {darkMode
		? 'bg-slate-900 text-slate-100'
		: 'bg-gradient-to-br from-amber-50 via-blue-50 to-orange-50 text-slate-800'}"
>
	<header
		class="sticky top-0 z-50 border-b px-4 py-4 backdrop-blur-md transition-colors duration-300 sm:px-6 {darkMode
			? 'border-slate-700/50 bg-slate-900/85'
			: 'border-slate-900/5 bg-amber-50/85'}"
	>
		<div class="mx-auto flex max-w-5xl items-center justify-between">
			<div class="flex items-center gap-2">
				<span class="text-2xl drop-shadow-sm">🎁</span>
				<span class="text-xl font-bold tracking-tight text-rose-500">{m.app_name()}</span>
			</div>
			<div class="flex items-center gap-3">
				<!-- Dark mode toggle -->
				<button
					type="button"
					onclick={toggleDarkMode}
					class="flex h-9 w-9 items-center justify-center rounded-lg transition-all {darkMode
						? 'bg-slate-800 text-yellow-400 hover:bg-slate-700'
						: 'bg-white text-slate-600 shadow-sm hover:bg-slate-50'}"
					aria-label="Toggle dark mode"
				>
					{#if darkMode}
						<svg
							class="h-5 w-5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
							/>
						</svg>
					{:else}
						<svg
							class="h-5 w-5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
							/>
						</svg>
					{/if}
				</button>
				<!-- Language switcher -->
				<div
					class="flex items-center gap-1 rounded-xl p-1 shadow-sm transition-colors {darkMode
						? 'bg-slate-800'
						: 'bg-white'}"
				>
					<button
						type="button"
						class="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all {getLocale() ===
						'en'
							? 'bg-rose-500 text-white shadow-sm'
							: darkMode
								? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200'
								: 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'}"
						onclick={() => switchLocale('en')}
					>
						<span>🇬🇧</span>
						<span class="hidden sm:inline">English</span>
					</button>
					<button
						type="button"
						class="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all {getLocale() ===
						'pl'
							? 'bg-rose-500 text-white shadow-sm'
							: darkMode
								? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200'
								: 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'}"
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
		<!-- Hero Section -->
		<section class="py-8 sm:py-12">
			<div class="mx-auto max-w-3xl text-center">
				<h1
					class="mb-4 text-4xl font-bold leading-tight tracking-tight sm:text-5xl {darkMode
						? 'text-white'
						: 'text-slate-800'}"
				>
					{m.tagline()}
				</h1>
				<p class="mx-auto mb-6 max-w-xl text-lg {darkMode ? 'text-slate-400' : 'text-slate-500'}">
					{m.hero_description()}
				</p>
				<div class="flex flex-wrap justify-center gap-2.5">
					<span
						class="inline-flex items-center gap-1.5 rounded-full border px-3.5 py-2 text-sm font-medium shadow-sm transition-colors {darkMode
							? 'border-slate-700 bg-slate-800 text-slate-300'
							: 'border-rose-500/15 bg-white text-slate-700'}"
					>
						<span class="text-xs text-emerald-500">✓</span>
						{m.badge_no_login()}
					</span>
					<span
						class="inline-flex items-center gap-1.5 rounded-full border px-3.5 py-2 text-sm font-medium shadow-sm transition-colors {darkMode
							? 'border-slate-700 bg-slate-800 text-slate-300'
							: 'border-rose-500/15 bg-white text-slate-700'}"
					>
						<span class="text-xs text-emerald-500">✓</span>
						{m.badge_free()}
					</span>
					<span
						class="inline-flex items-center gap-1.5 rounded-full border px-3.5 py-2 text-sm font-medium shadow-sm transition-colors {darkMode
							? 'border-slate-700 bg-slate-800 text-slate-300'
							: 'border-rose-500/15 bg-white text-slate-700'}"
					>
						<span class="text-xs">🔒</span>
						{m.badge_private()}
					</span>
				</div>
			</div>
		</section>

		<!-- Steps + Form Section -->
		<section class="py-6">
			<div class="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1fr_420px] lg:items-start lg:gap-12">
				<!-- Steps (vertical on left) -->
				<div>
					<h2
						class="mb-6 text-xl font-bold tracking-tight lg:text-2xl {darkMode
							? 'text-white'
							: 'text-slate-800'}"
					>
						{m.how_it_works_title()}
					</h2>
					<div class="flex flex-col gap-4">
						<article
							class="flex items-start gap-4 rounded-2xl border p-5 shadow-sm transition-all hover:shadow-md {darkMode
								? 'border-slate-700/50 bg-slate-800/50'
								: 'border-slate-900/5 bg-white'}"
						>
							<div
								class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 text-lg font-bold text-white shadow-md shadow-emerald-400/35"
							>
								1
							</div>
							<div>
								<h3
									class="mb-1 text-base font-semibold {darkMode ? 'text-white' : 'text-slate-800'}"
								>
									{m.step1_title()}
								</h3>
								<p class="text-sm leading-relaxed {darkMode ? 'text-slate-400' : 'text-slate-500'}">
									{m.step1_desc()}
								</p>
							</div>
						</article>
						<article
							class="flex items-start gap-4 rounded-2xl border p-5 shadow-sm transition-all hover:shadow-md {darkMode
								? 'border-slate-700/50 bg-slate-800/50'
								: 'border-slate-900/5 bg-white'}"
						>
							<div
								class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-lg font-bold text-white shadow-md shadow-orange-400/35"
							>
								2
							</div>
							<div>
								<h3
									class="mb-1 text-base font-semibold {darkMode ? 'text-white' : 'text-slate-800'}"
								>
									{m.step2_title()}
								</h3>
								<p class="text-sm leading-relaxed {darkMode ? 'text-slate-400' : 'text-slate-500'}">
									{m.step2_desc()}
								</p>
							</div>
						</article>
						<article
							class="flex items-start gap-4 rounded-2xl border p-5 shadow-sm transition-all hover:shadow-md {darkMode
								? 'border-slate-700/50 bg-slate-800/50'
								: 'border-slate-900/5 bg-white'}"
						>
							<div
								class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-rose-400 to-rose-500 text-lg font-bold text-white shadow-md shadow-rose-400/35"
							>
								3
							</div>
							<div>
								<h3
									class="mb-1 text-base font-semibold {darkMode ? 'text-white' : 'text-slate-800'}"
								>
									{m.step3_title()}
								</h3>
								<p class="text-sm leading-relaxed {darkMode ? 'text-slate-400' : 'text-slate-500'}">
									{m.step3_desc()}
								</p>
							</div>
						</article>
					</div>
				</div>

				<!-- Form Card (on right) -->
				<div
					class="rounded-2xl border p-6 shadow-lg transition-colors sm:p-8 {darkMode
						? 'border-slate-700/50 bg-slate-800/80 shadow-slate-900/50'
						: 'border-slate-900/5 bg-white shadow-slate-900/5'}"
				>
					<h2
						class="mb-6 text-center text-xl font-semibold {darkMode
							? 'text-white'
							: 'text-slate-800'}"
					>
						{m.form_title()}
					</h2>
					<form
						onsubmit={(e: Event) => {
							e.preventDefault();
							handleSubmit();
						}}
					>
						<div class="mb-4">
							<label
								for="eventName"
								class="mb-1.5 block text-sm font-medium {darkMode
									? 'text-slate-300'
									: 'text-slate-600'}"
							>
								{m.label_event_name()}
							</label>
							<input
								type="text"
								id="eventName"
								bind:value={eventName}
								placeholder={m.placeholder_event_name()}
								class="w-full rounded-xl border-[1.5px] px-4 py-3 text-base transition-all focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none {darkMode
									? 'border-slate-600 bg-slate-700/50 text-white placeholder-slate-500 focus:bg-slate-700'
									: 'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:bg-white'}"
							/>
						</div>

						<div class="mb-4">
							<label
								for="maxAmount"
								class="mb-1.5 block text-sm font-medium {darkMode
									? 'text-slate-300'
									: 'text-slate-600'}"
							>
								{m.label_max_amount()}
								<span class="font-normal {darkMode ? 'text-slate-500' : 'text-slate-400'}">
									{m.label_max_amount_optional()}</span
								>
							</label>
							<div class="flex">
								<input
									type="number"
									id="maxAmount"
									bind:value={maxAmount}
									placeholder={m.placeholder_max_amount()}
									min="1"
									class="w-full rounded-l-xl border-[1.5px] border-r-0 px-4 py-3 text-base transition-all focus:relative focus:z-10 focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none {darkMode
										? 'border-slate-600 bg-slate-700/50 text-white placeholder-slate-500 focus:bg-slate-700'
										: 'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:bg-white'}"
								/>
								<span
									class="flex items-center rounded-r-xl border-[1.5px] border-l-0 px-4 text-sm font-medium {darkMode
										? 'border-slate-600 bg-slate-700 text-slate-400'
										: 'border-slate-200 bg-slate-100 text-slate-500'}"
								>
									{m.currency_suffix()}
								</span>
							</div>
						</div>

						<div class="mb-4">
							<label
								for="eventDate"
								class="mb-1.5 block text-sm font-medium {darkMode
									? 'text-slate-300'
									: 'text-slate-600'}"
							>
								{m.label_date()}
								<span class="font-normal {darkMode ? 'text-slate-500' : 'text-slate-400'}"
									>{m.label_date_optional()}</span
								>
							</label>
							<input
								type="date"
								id="eventDate"
								bind:value={eventDate}
								class="w-full rounded-xl border-[1.5px] px-4 py-3 text-base transition-all focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none {darkMode
									? 'border-slate-600 bg-slate-700/50 text-white focus:bg-slate-700'
									: 'border-slate-200 bg-slate-50 text-slate-800 focus:bg-white'}"
							/>
						</div>

						<div class="mb-4">
							<label
								for="participants"
								class="mb-1.5 block text-sm font-medium {darkMode
									? 'text-slate-300'
									: 'text-slate-600'}"
							>
								{m.label_participants()}
							</label>
							<textarea
								id="participants"
								bind:value={participantsInput}
								placeholder={m.placeholder_participants()}
								rows="3"
								class="w-full resize-none rounded-xl border-[1.5px] px-4 py-3 text-base transition-all focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none {darkMode
									? 'border-slate-600 bg-slate-700/50 text-white placeholder-slate-500 focus:bg-slate-700'
									: 'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:bg-white'}"
							></textarea>
							<span class="mt-1.5 block text-xs {darkMode ? 'text-slate-500' : 'text-slate-400'}"
								>{m.participants_hint()}</span
							>

							{#if participants.length > 0}
								<div class="participants-chips-wrapper mt-3">
									<span
										class="mb-2 block text-xs font-medium {darkMode
											? 'text-slate-400'
											: 'text-slate-500'}"
									>
										{m.participants_count({ count: participants.length })}
									</span>
									<div class="participants-chips">
										{#each participants as participant, i (i)}
											<span
												class="participants-chip {darkMode ? 'participants-chip--dark' : ''}"
												style="animation-delay: {i * 30}ms"
											>
												{participant}
											</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>

						<button
							type="submit"
							class="w-full cursor-pointer rounded-xl bg-gradient-to-r from-orange-400 to-rose-500 px-6 py-3.5 text-base font-semibold text-white shadow-md shadow-rose-500/30 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-rose-500/40 active:translate-y-0 active:shadow-md"
						>
							{m.button_create()}
						</button>
					</form>

					<div
						class="my-5 flex items-center gap-4 text-sm {darkMode
							? 'text-slate-500'
							: 'text-slate-400'}"
					>
						<span class="h-px flex-1 {darkMode ? 'bg-slate-700' : 'bg-slate-200'}"></span>
						<span>{m.or_separator()}</span>
						<span class="h-px flex-1 {darkMode ? 'bg-slate-700' : 'bg-slate-200'}"></span>
					</div>

					<button
						type="button"
						class="w-full cursor-pointer rounded-xl border-[1.5px] bg-transparent px-6 py-3 text-base font-medium transition-all hover:border-rose-500 hover:bg-rose-500/5 hover:text-rose-500 {darkMode
							? 'border-slate-600 text-slate-400'
							: 'border-slate-200 text-slate-600'}"
						onclick={handleDemo}
					>
						{m.button_demo()}
					</button>
				</div>
			</div>
		</section>
	</main>

	<footer
		class="border-t px-4 py-8 backdrop-blur-sm transition-colors sm:px-6 {darkMode
			? 'border-slate-700/50 bg-slate-800/50'
			: 'border-slate-900/5 bg-white/50'}"
	>
		<div
			class="mx-auto flex max-w-5xl flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left"
		>
			<p class="text-sm {darkMode ? 'text-slate-500' : 'text-slate-500'}">
				© {new Date().getFullYear()} Created by Dawid Hanrahan
			</p>
			<div class="flex items-center gap-5">
				<a
					href="https://dawidhanrahan.com"
					target="_blank"
					rel="noopener noreferrer"
					class="text-sm font-medium transition-colors hover:text-rose-500 {darkMode
						? 'text-slate-400'
						: 'text-slate-500'}"
				>
					dawidhanrahan.com
				</a>
				<a
					href="https://github.com/dawidhanrahan"
					target="_blank"
					rel="noopener noreferrer"
					class="transition-colors hover:text-rose-500 {darkMode
						? 'text-slate-500'
						: 'text-slate-400'}"
					aria-label="GitHub"
				>
					<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
						<path
							fill-rule="evenodd"
							d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
							clip-rule="evenodd"
						/>
					</svg>
				</a>
			</div>
		</div>
	</footer>
</div>

<style>
	.participants-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.participants-chip {
		display: inline-flex;
		align-items: center;
		padding: 0.375rem 0.75rem;
		font-size: 0.8125rem;
		font-weight: 500;
		line-height: 1;
		color: #475569;
		background-color: #f1f5f9;
		border: 1px solid #e2e8f0;
		border-radius: 9999px;
		animation: chip-pop-in 0.2s ease-out both;
	}

	.participants-chip--dark {
		color: #cbd5e1;
		background-color: #334155;
		border-color: #475569;
	}

	@keyframes chip-pop-in {
		from {
			opacity: 0;
			transform: scale(0.8);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}
</style>
