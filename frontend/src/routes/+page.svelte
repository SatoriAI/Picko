<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { fetchJson } from '$lib/api/client';
	import {
		PageLayout,
		Card,
		Badge,
		StepCard,
		Input,
		Select,
		FormLabel,
		FormError,
		Button
	} from '$lib/components';

	let eventName = $state('');
	let maxAmount = $state('');
	let currency = $state<'PLN' | 'USD' | 'EUR'>('PLN');
	let eventDate = $state('');
	let registrationDeadline = $state('');
	let isSubmitting = $state(false);

	// Form validation errors
	let errors = $state<{
		eventName?: string;
		maxAmount?: string;
		registrationDeadline?: string;
		form?: string;
	}>({});

	// Currency options for select
	const currencyOptions: Array<{ value: 'PLN' | 'USD' | 'EUR'; label: string }> = [
		{ value: 'PLN', label: 'PLN' },
		{ value: 'USD', label: 'USD' },
		{ value: 'EUR', label: 'EUR' }
	];

	function validateForm(): boolean {
		const newErrors: typeof errors = {};

		// Validate event name
		if (!eventName.trim()) {
			newErrors.eventName = m.validation_event_name_required();
		}

		// Validate max amount (if provided)
		const maxAmountRaw = String(maxAmount ?? '');
		const maxAmountValue = maxAmountRaw.trim() ? Number(maxAmountRaw) : null;
		if (maxAmountValue !== null && (!Number.isFinite(maxAmountValue) || maxAmountValue <= 0)) {
			newErrors.maxAmount = m.validation_max_amount_invalid();
		}

		// Validate deadline
		if (!registrationDeadline) {
			newErrors.registrationDeadline = m.validation_deadline_required();
		} else {
			const deadlineDate = new Date(registrationDeadline);
			if (deadlineDate <= new Date()) {
				newErrors.registrationDeadline = m.validation_deadline_future();
			}
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	async function handleSubmit() {
		if (!validateForm()) {
			return;
		}

		const maxAmountRaw = String(maxAmount ?? '');
		const maxAmountValue = maxAmountRaw.trim() ? Number(maxAmountRaw) : null;

		isSubmitting = true;
		errors = {};

		try {
			const created = await fetchJson<{ id: number; registration_token: string }>('/api/event', {
				method: 'POST',
				body: JSON.stringify({
					name: eventName.trim(),
					max_amount: maxAmountValue,
					date: eventDate || null,
					currency: maxAmountValue === null ? null : currency,
					registration_deadline: new Date(registrationDeadline).toISOString()
				})
			});

			// Redirect to registration page so the creator can join as participant
			await goto(resolve(`/register/${created.registration_token}`));
		} catch (err) {
			console.error('Create event request failed', err);
			errors = { form: m.validation_error() };
		} finally {
			isSubmitting = false;
		}
	}

	// Steps data - updated for new flow
	const steps = [
		{
			step: 1,
			title: () => m.step1_title(),
			desc: () => m.step1_desc(),
			color: 'emerald' as const
		},
		{ step: 2, title: () => m.step2_title(), desc: () => m.step2_desc(), color: 'amber' as const },
		{ step: 3, title: () => m.step3_title(), desc: () => m.step3_desc(), color: 'rose' as const }
	];

	// Badges data
	const badges = [
		{ icon: '✓', iconColor: 'text-emerald-500', message: () => m.badge_no_login() },
		{ icon: '✓', iconColor: 'text-emerald-500', message: () => m.badge_free() },
		{ icon: '🔒', iconColor: '', message: () => m.badge_private() }
	];
</script>

<svelte:head>
	<title>{m.tagline()}</title>
</svelte:head>

<PageLayout>
	<!-- Hero Section -->
	<section class="py-8 sm:py-12">
		<div class="mx-auto max-w-3xl text-center">
			<h1
				class="mb-4 text-4xl font-bold leading-tight tracking-tight text-slate-800 sm:text-5xl dark:text-white"
			>
				{m.tagline()}
			</h1>
			<p class="mx-auto mb-6 max-w-xl text-lg text-slate-500 dark:text-slate-400">
				{m.hero_description()}
			</p>
			<div class="flex flex-wrap justify-center gap-2.5">
				{#each badges as badge, i (i)}
					<Badge icon={badge.icon} iconColor={badge.iconColor}>
						{badge.message()}
					</Badge>
				{/each}
			</div>
		</div>
	</section>

	<!-- Steps + Form Section -->
	<section class="py-6">
		<div class="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1fr_420px] lg:items-start lg:gap-12">
			<!-- Steps (vertical on left) -->
			<div>
				<h2
					class="mb-6 text-xl font-bold tracking-tight text-slate-800 lg:text-2xl dark:text-white"
				>
					{m.how_it_works_title()}
				</h2>
				<div class="flex flex-col gap-4">
					{#each steps as s (s.step)}
						<StepCard step={s.step} title={s.title()} description={s.desc()} color={s.color} />
					{/each}
				</div>
			</div>

			<!-- Form Card (on right) -->
			<Card>
				<h2 class="mb-6 text-center text-xl font-semibold text-slate-800 dark:text-white">
					{m.form_title()}
				</h2>

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
						<FormLabel for="eventName">{m.label_event_name()}</FormLabel>
						<Input
							id="eventName"
							bind:value={eventName}
							placeholder={m.placeholder_event_name()}
							error={!!errors.eventName}
						/>
						<FormError message={errors.eventName} />
					</div>

					<div class="mb-4">
						<FormLabel for="maxAmount" optional={m.label_max_amount_optional()}>
							{m.label_max_amount()}
						</FormLabel>
						<div class="flex">
							<Input
								type="number"
								id="maxAmount"
								bind:value={maxAmount}
								placeholder={m.placeholder_max_amount()}
								min="1"
								error={!!errors.maxAmount}
								class="no-number-spin rounded-r-none border-r-0"
							/>
							<Select
								id="currency"
								bind:value={currency}
								options={currencyOptions}
								aria-label="Currency"
								class="w-[120px] rounded-l-none border-l-0"
							/>
						</div>
						<FormError message={errors.maxAmount} />
					</div>

					<div class="mb-4">
						<FormLabel for="eventDate" optional={m.label_date_optional()}>
							{m.label_date()}
						</FormLabel>
						<Input type="date" id="eventDate" bind:value={eventDate} />
					</div>

					<div class="mb-4">
						<FormLabel for="registrationDeadline">{m.label_deadline()}</FormLabel>
						<Input
							type="datetime-local"
							id="registrationDeadline"
							bind:value={registrationDeadline}
							error={!!errors.registrationDeadline}
						/>
						{#if errors.registrationDeadline}
							<FormError message={errors.registrationDeadline} />
						{:else}
							<span class="mt-1.5 block text-xs text-slate-400 dark:text-slate-500">
								{m.label_deadline_hint()}
							</span>
						{/if}
					</div>

					<Button type="submit" disabled={isSubmitting}>
						{isSubmitting ? m.creating() : m.button_create()}
					</Button>
				</form>
			</Card>
		</div>
	</section>
</PageLayout>

<style>
	/* Remove number input arrows (spinners) for max amount. */
	:global(input.no-number-spin::-webkit-outer-spin-button),
	:global(input.no-number-spin::-webkit-inner-spin-button) {
		-webkit-appearance: none;
		margin: 0;
	}

	:global(input.no-number-spin) {
		appearance: textfield;
		-moz-appearance: textfield;
	}
</style>
