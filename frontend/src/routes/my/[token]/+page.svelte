<script lang="ts">
	import { resolve } from '$app/paths';
	import * as m from '$lib/paraglide/messages';
	import { DEFAULT_CURRENCY } from '$lib/constants';
	import {
		PageLayout,
		GiftBoxReveal,
		CountdownTimer,
		CopyButton,
		ActionLink
	} from '$lib/components';
	import type { MyStatusData } from '$lib/types';

	// Props from loader
	let { data } = $props();
	const status: MyStatusData = data;

	// Loading state when countdown reaches zero
	let isLoadingDraw = $state(false);

	// Derived states
	let deadlinePassed = $derived(new Date(status.event.registration_deadline) <= new Date());
	let drawFailed = $derived(deadlinePassed && !status.event.is_draw_complete && !status.assignment);
	let myLink = $derived(typeof window !== 'undefined' ? window.location.href : '');

	// Handle countdown completion
	function handleCountdownComplete() {
		isLoadingDraw = true;
		setTimeout(() => {
			window.location.reload();
		}, 1500);
	}

	function getCalendarUrl() {
		if (!status.event.date) return null;
		const date = new Date(status.event.date);
		const dateStr = date
			.toISOString()
			.replace(/-|:|\.\d+/g, '')
			.slice(0, 8);
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
			<div
				class="mb-6 h-12 w-12 animate-spin rounded-full border-4 border-orange-200 border-t-orange-500"
			></div>
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
			<GiftBoxReveal
				giverName={status.participant_name}
				receiverName={status.assignment.receiver_name}
				receiverWishlist={status.assignment.receiver_wishlist}
				eventName={status.event.name}
				eventDate={status.event.date}
				maxAmount={status.event.max_amount}
				currency={status.event.currency ?? DEFAULT_CURRENCY}
			/>

			<!-- Action links (shown after reveal completes in GiftBoxReveal) -->
			<div class="mt-6 flex flex-wrap items-center justify-center gap-3">
				{#if status.event.date}
					{@const calendarUrl = getCalendarUrl()}
					{#if calendarUrl}
						<ActionLink href={calendarUrl}>
							<span>📅</span>
							{m.my_add_to_calendar()}
						</ActionLink>
					{/if}
				{/if}
				<ActionLink href={resolve(`/event/${status.event.id}`)}>
					<span>👥</span>
					{m.my_view_event_button()}
				</ActionLink>
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

				<!-- Countdown Timer -->
				<div class="mb-4">
					<CountdownTimer
						deadline={status.event.registration_deadline}
						onComplete={handleCountdownComplete}
						variant="minimal"
					/>
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
						<CopyButton text={myLink} size="sm" label={m.my_copy_link()} />
					</div>
				</div>
			</div>
		</div>
	{/if}
</PageLayout>
