<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { formatDateLong } from '$lib/utils/date';
	import { fetchJson } from '$lib/api/client';
	import { DEFAULT_CURRENCY } from '$lib/constants';
	import {
		PageLayout,
		Card,
		Input,
		TextArea,
		Select,
		FormLabel,
		FormError,
		Button,
		Chip
	} from '$lib/components';
	import type { RegistrationEventData } from '$lib/types';

	// Props from loader
	let { data } = $props();
	const event: RegistrationEventData = data.event;
	const token: string = data.token;

	// Form state
	let name = $state('');
	let email = $state('');
	let language = $state(getLocale() === 'pl' ? 'pl' : 'en');
	let wishlist = $state('');
	let isSubmitting = $state(false);

	// Form validation errors
	let errors = $state<{
		name?: string;
		form?: string;
	}>({});

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

	function validateForm(): boolean {
		const newErrors: typeof errors = {};

		if (!name.trim()) {
			newErrors.name = m.validation_name_required();
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	async function handleSubmit() {
		if (!validateForm()) {
			return;
		}

		isSubmitting = true;
		errors = {};

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
			errors = { form: m.registration_failed() };
		} finally {
			isSubmitting = false;
		}
	}
</script>

<svelte:head>
	<title>{m.register_title()}: {event.name}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<section class="py-6 sm:py-8">
		<div class="mx-auto max-w-xl">
			<!-- Event Info Header -->
			<div class="mb-6 text-center">
				<div
					class="mb-3 inline-block rounded-full bg-gradient-to-r from-orange-500 to-pink-500 px-4 py-1.5 text-sm font-medium text-white"
				>
					🎄 {event.name}
				</div>
				<h1 class="mb-2 text-2xl font-bold text-slate-800 sm:text-3xl dark:text-white">
					{m.register_title()}
				</h1>
				<p class="text-slate-500 dark:text-slate-400">
					{m.register_subtitle()}
				</p>
			</div>

			{#if deadlinePassed}
				<!-- Registration closed -->
				<Card class="p-6 text-center">
					<div class="mb-4 text-5xl">⏰</div>
					<h2 class="mb-2 text-xl font-semibold text-slate-800 dark:text-white">
						{m.registration_closed_title()}
					</h2>
					<p class="text-slate-500 dark:text-slate-400">
						{m.registration_closed_desc()}
					</p>
				</Card>
			{:else}
				<!-- Event Details -->
				<Card class="mb-6 p-4">
					<div class="grid gap-3 text-sm sm:grid-cols-2">
						{#if event.date}
							<div class="flex items-center gap-2 text-slate-600 dark:text-slate-300">
								<span>📅</span>
								<span>
									{m.join_event_date()}: <strong>{formatDateLong(event.date, getLocale())}</strong>
								</span>
							</div>
						{/if}
						{#if event.maxAmount}
							<div class="flex items-center gap-2 text-slate-600 dark:text-slate-300">
								<span>💰</span>
								<span>
									{m.join_budget()}:
									<strong>{event.maxAmount} {event.currency ?? DEFAULT_CURRENCY}</strong>
								</span>
							</div>
						{/if}
						<div class="flex items-center gap-2 text-slate-600 dark:text-slate-300">
							<span>⏰</span>
							<span>
								{m.deadline_label()}:
								<strong>{formatDateLong(event.registrationDeadline, getLocale())}</strong>
							</span>
						</div>
						<div class="flex items-center gap-2 text-slate-600 dark:text-slate-300">
							<span>👥</span>
							<span>
								{m.registered_count({ count: event.participants.length })}
							</span>
						</div>
					</div>
				</Card>

				<!-- Registration Form -->
				<Card class="p-6">
					<!-- Form-level error -->
					{#if errors.form}
						<div
							class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-400"
						>
							{errors.form}
						</div>
					{/if}

					<form
						onsubmit={(e) => {
							e.preventDefault();
							handleSubmit();
						}}
					>
						<div class="mb-4">
							<FormLabel for="name">{m.label_name()}</FormLabel>
							<Input
								id="name"
								bind:value={name}
								placeholder={m.placeholder_name()}
								error={!!errors.name}
							/>
							<FormError message={errors.name} />
						</div>

						<div class="mb-4">
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

						<div class="mb-4">
							<FormLabel for="language">{m.label_language()}</FormLabel>
							<Select id="language" bind:value={language} options={languageOptions} />
						</div>

						<div class="mb-6">
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

						<Button type="submit" disabled={isSubmitting} class="w-full">
							{isSubmitting ? m.registering() : m.register_button()}
						</Button>
					</form>
				</Card>

				<!-- Already registered participants -->
				{#if event.participants.length > 0}
					<div class="mt-6">
						<h3
							class="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
						>
							{m.already_registered()}
						</h3>
						<div class="flex flex-wrap gap-2">
							{#each event.participants as participant (participant.id)}
								<Chip>{participant.name}</Chip>
							{/each}
						</div>
					</div>
				{/if}
			{/if}
		</div>
	</section>
</PageLayout>
