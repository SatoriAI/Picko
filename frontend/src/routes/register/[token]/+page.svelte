<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { formatDateLong } from '$lib/utils/date';
	import { fetchJson } from '$lib/api/client';
	import {
		PageLayout,
		Card,
		Input,
		TextArea,
		Select,
		FormLabel,
		Button,
		Chip
	} from '$lib/components';
	import type { EventData } from './+page';

	// Props from loader
	let { data } = $props();
	const event: EventData = data.event;
	const token: string = data.token;

	// Form state
	let name = $state('');
	let email = $state('');
	let language = $state(getLocale() === 'pl' ? 'pl' : 'en');
	let wishlist = $state('');
	let isSubmitting = $state(false);

	// Language options
	const languageOptions = [
		{ value: 'en', label: 'English' },
		{ value: 'pl', label: 'Polski' }
	];

	// Check if registration is still open
	const deadlinePassed = $derived(new Date(event.registrationDeadline) <= new Date());

	// Parse wishlist items for preview
	let wishlistItems = $derived(
		wishlist
			.split(',')
			.map((item) => item.trim())
			.filter((item) => item.length > 0)
	);

	async function handleSubmit() {
		if (!name.trim()) {
			alert(m.validation_error());
			return;
		}

		isSubmitting = true;
		try {
			const result = await fetchJson<{ event_id: number; access_token: string }>(
				`/api/event/register/${token}`,
				{
					method: 'POST',
					body: JSON.stringify({
						name: name.trim(),
						email: email.trim() || null,
						language,
						wishlist: wishlist.trim() || null
					})
				}
			);

			// Redirect to personal status page
			await goto(resolve(`/my/${result.access_token}`));
		} catch (err) {
			console.error('Registration failed', err);
			alert(m.registration_failed());
		} finally {
			isSubmitting = false;
		}
	}
</script>

<svelte:head>
	<title>{m.register_title()} - {event.name}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<section class="py-6 sm:py-8">
		<div class="mx-auto max-w-3xl">
			<!-- Event Info Header -->
			<div class="mb-8 text-center">
				<div
					class="mb-4 inline-block rounded-full bg-gradient-to-r from-orange-500 to-pink-500 px-4 py-1.5 text-sm font-medium text-white shadow-lg shadow-orange-500/25"
				>
					🎄 {event.name}
				</div>
				<h1 class="mb-3 text-2xl font-bold text-slate-800 sm:text-3xl dark:text-white">
					{m.register_title()}
				</h1>
				<p class="text-slate-500 dark:text-slate-400">
					{m.register_subtitle()}
				</p>
			</div>

			{#if deadlinePassed}
				<!-- Registration closed -->
				<Card class="p-8 text-center sm:p-10">
					<div class="mb-5 text-6xl">⏰</div>
					<h2 class="mb-3 text-xl font-bold text-slate-800 sm:text-2xl dark:text-white">
						{m.registration_closed_title()}
					</h2>
					<p class="text-slate-500 dark:text-slate-400">
						{m.registration_closed_desc()}
					</p>
				</Card>
			{:else}
				<!-- Event Details -->
				<Card class="mb-6 p-5">
					<div class="grid gap-4 text-sm sm:grid-cols-2">
						{#if event.date}
							<div
								class="flex items-center gap-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-700/50"
							>
								<span class="text-lg">📅</span>
								<div>
									<span class="block text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
										{m.join_event_date()}
									</span>
									<span class="font-semibold text-slate-700 dark:text-slate-200">
										{formatDateLong(event.date, getLocale())}
									</span>
								</div>
							</div>
						{/if}
						{#if event.maxAmount}
							<div
								class="flex items-center gap-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-700/50"
							>
								<span class="text-lg">💰</span>
								<div>
									<span class="block text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
										{m.join_budget()}
									</span>
									<span class="font-semibold text-slate-700 dark:text-slate-200">
										{event.maxAmount} {event.currency ?? 'PLN'}
									</span>
								</div>
							</div>
						{/if}
						<div
							class="flex items-center gap-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-700/50"
						>
							<span class="text-lg">⏰</span>
							<div>
								<span class="block text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
									{m.deadline_label()}
								</span>
								<span class="font-semibold text-slate-700 dark:text-slate-200">
									{formatDateLong(event.registrationDeadline, getLocale())}
								</span>
							</div>
						</div>
						<div
							class="flex items-center gap-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-700/50"
						>
							<span class="text-lg">👥</span>
							<div>
								<span class="block text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
									{m.admin_participants_label()}
								</span>
								<span class="font-semibold text-slate-700 dark:text-slate-200">
									{m.registered_count({ count: event.participants.length })}
								</span>
							</div>
						</div>
					</div>
				</Card>

				<!-- Registration Form -->
				<Card class="p-6 sm:p-8">
					<form
						onsubmit={(e) => {
							e.preventDefault();
							handleSubmit();
						}}
						class="space-y-5"
					>
						<div>
							<FormLabel for="name">{m.label_name()}</FormLabel>
							<Input id="name" bind:value={name} placeholder={m.placeholder_name()} required />
						</div>

						<div>
							<FormLabel for="email" optional={m.label_optional()}>
								{m.label_email()}
							</FormLabel>
							<Input
								type="email"
								id="email"
								bind:value={email}
								placeholder={m.placeholder_email()}
							/>
							<span class="mt-1.5 block text-xs text-slate-400 dark:text-slate-500">
								{m.email_hint()}
							</span>
						</div>

						<div>
							<FormLabel for="language">{m.label_language()}</FormLabel>
							<Select id="language" bind:value={language} options={languageOptions} />
						</div>

						<div>
							<FormLabel for="wishlist" optional={m.label_optional()}>
								{m.label_wishlist()}
							</FormLabel>
							<TextArea
								id="wishlist"
								bind:value={wishlist}
								placeholder={m.placeholder_wishlist()}
								rows={3}
							/>
							<span class="mt-1.5 block text-xs text-slate-400 dark:text-slate-500">
								{m.wishlist_hint()}
							</span>

							{#if wishlistItems.length > 0}
								<div class="mt-3">
									<span class="mb-2 block text-xs font-medium text-slate-500 dark:text-slate-400">
										{m.wishlist_preview()}
									</span>
									<div class="flex flex-wrap gap-2">
										{#each wishlistItems as item, i (i)}
											<Chip animated delay={i * 30}>🎁 {item}</Chip>
										{/each}
									</div>
								</div>
							{/if}
						</div>

						<div class="pt-2">
							<Button type="submit" disabled={isSubmitting} class="w-full py-3 text-base">
								{isSubmitting ? m.registering() : m.register_button()}
							</Button>
						</div>
					</form>
				</Card>

				<!-- Already registered participants -->
				{#if event.participants.length > 0}
					<Card class="mt-6 p-5">
						<h3
							class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300"
						>
							<span>✨</span>
							{m.already_registered()}
						</h3>
						<div class="flex flex-wrap gap-2">
							{#each event.participants as participant (participant.id)}
								<Chip>{participant.name}</Chip>
							{/each}
						</div>
					</Card>
				{/if}
			{/if}
		</div>
	</section>
</PageLayout>
