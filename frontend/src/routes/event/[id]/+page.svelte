<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { formatDateLong } from '$lib/utils/date';
	import { DEFAULT_CURRENCY } from '$lib/constants';
	import {
		PageLayout,
		Card,
		Chip,
		Input,
		CheckIcon,
		CountdownTimer,
		WishlistDisplay,
		StepBadge,
		CopyButton
	} from '$lib/components';
	import type { EventData } from '$lib/types';

	// Props from loader
	let { data } = $props();

	// Event data from loader (reactive to allow updates)
	let event = $state<EventData>(data.event);

	// Derived states
	let deadlinePassed = $derived(new Date(event.registrationDeadline) <= new Date());
	let registrationUrl = $derived(
		typeof window !== 'undefined'
			? `${window.location.origin}/register/${event.registrationToken}`
			: `/register/${event.registrationToken}`
	);

	// Handle countdown completion
	function handleCountdownComplete() {
		window.location.reload();
	}
</script>

<svelte:head>
	<title>{m.admin_event_dashboard()}: {event.name}</title>
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
				<StepBadge step={1} color="emerald" />
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
							{event.maxAmount ? (event.currency ?? DEFAULT_CURRENCY) : ''}
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
					<StepBadge step={2} color="amber" />
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
					<CopyButton text={registrationUrl} />
				</div>

				<!-- Countdown Timer -->
				<CountdownTimer
					deadline={event.registrationDeadline}
					onComplete={handleCountdownComplete}
					variant="gradient"
				/>
				<p class="mt-4 text-center text-sm text-white/90">
					{m.draw_at_deadline()}
				</p>
			</Card>
		{:else if !event.isDrawComplete}
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

		<!-- Registered Participants with Wishlists (always visible when there are participants) -->
		{#if event.participants.length > 0}
			<Card class="p-6">
				<h2
					class="mb-4 flex items-center gap-3 text-lg font-semibold text-slate-800 dark:text-white"
				>
					<StepBadge step={!deadlinePassed || !event.isDrawComplete ? 3 : 2} color="rose" />
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
									<WishlistDisplay
										wishlist={participant.wishlist}
										variant="compact"
										label={m.wishlist_label()}
									/>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</Card>
		{/if}
	</div>
</PageLayout>
