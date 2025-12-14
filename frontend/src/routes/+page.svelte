<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { darkMode } from '$lib/stores/theme';
	import {
		PageLayout,
		Card,
		Badge,
		StepCard,
		Input,
		TextArea,
		FormLabel,
		Button,
		Chip
	} from '$lib/components';

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

	// Steps data
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

<PageLayout>
	<!-- Hero Section -->
	<section class="py-8 sm:py-12">
		<div class="mx-auto max-w-3xl text-center">
			<h1
				class="mb-4 text-4xl font-bold leading-tight tracking-tight sm:text-5xl {$darkMode
					? 'text-white'
					: 'text-slate-800'}"
			>
				{m.tagline()}
			</h1>
			<p class="mx-auto mb-6 max-w-xl text-lg {$darkMode ? 'text-slate-400' : 'text-slate-500'}">
				{m.hero_description()}
			</p>
			<div class="flex flex-wrap justify-center gap-2.5">
				{#each badges as { icon, iconColor, message }}
					<Badge {icon} {iconColor}>
						{message()}
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
					class="mb-6 text-xl font-bold tracking-tight lg:text-2xl {$darkMode
						? 'text-white'
						: 'text-slate-800'}"
				>
					{m.how_it_works_title()}
				</h2>
				<div class="flex flex-col gap-4">
					{#each steps as { step, title, desc, color }}
						<StepCard {step} title={title()} description={desc()} {color} />
					{/each}
				</div>
			</div>

			<!-- Form Card (on right) -->
			<Card>
				<h2
					class="mb-6 text-center text-xl font-semibold {$darkMode
						? 'text-white'
						: 'text-slate-800'}"
				>
					{m.form_title()}
				</h2>
				<form
					onsubmit={(e) => {
						e.preventDefault();
						handleSubmit();
					}}
				>
					<div class="mb-4">
						<FormLabel for="eventName">{m.label_event_name()}</FormLabel>
						<Input id="eventName" bind:value={eventName} placeholder={m.placeholder_event_name()} />
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
								class="rounded-r-none border-r-0"
							/>
							<span
								class="flex items-center rounded-r-xl border-[1.5px] border-l-0 px-4 text-sm font-medium {$darkMode
									? 'border-slate-600 bg-slate-700 text-slate-400'
									: 'border-slate-200 bg-slate-100 text-slate-500'}"
							>
								{m.currency_suffix()}
							</span>
						</div>
					</div>

					<div class="mb-4">
						<FormLabel for="eventDate" optional={m.label_date_optional()}>
							{m.label_date()}
						</FormLabel>
						<Input type="date" id="eventDate" bind:value={eventDate} />
					</div>

					<div class="mb-4">
						<FormLabel for="participants">{m.label_participants()}</FormLabel>
						<TextArea
							id="participants"
							bind:value={participantsInput}
							placeholder={m.placeholder_participants()}
						/>
						<span class="mt-1.5 block text-xs {$darkMode ? 'text-slate-500' : 'text-slate-400'}">
							{m.participants_hint()}
						</span>

						{#if participants.length > 0}
							<div class="mt-3">
								<span
									class="mb-2 block text-xs font-medium {$darkMode
										? 'text-slate-400'
										: 'text-slate-500'}"
								>
									{m.participants_count({ count: participants.length })}
								</span>
								<div class="flex flex-wrap gap-2">
									{#each participants as participant, i (i)}
										<Chip animated delay={i * 30}>
											{participant}
										</Chip>
									{/each}
								</div>
							</div>
						{/if}
					</div>

					<Button type="submit">{m.button_create()}</Button>
				</form>

				<div
					class="my-5 flex items-center gap-4 text-sm {$darkMode
						? 'text-slate-500'
						: 'text-slate-400'}"
				>
					<span class="h-px flex-1 {$darkMode ? 'bg-slate-700' : 'bg-slate-200'}"></span>
					<span>{m.or_separator()}</span>
					<span class="h-px flex-1 {$darkMode ? 'bg-slate-700' : 'bg-slate-200'}"></span>
				</div>

				<Button variant="secondary" onclick={handleDemo}>{m.button_demo()}</Button>
			</Card>
		</div>
	</section>
</PageLayout>
