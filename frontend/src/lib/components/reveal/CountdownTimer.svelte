<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { onMount, onDestroy } from 'svelte';

	interface Props {
		deadline: string;
		/**
		 * Called when countdown reaches zero.
		 */
		onComplete?: () => void;
		/**
		 * Visual variant: 'gradient' shows colorful card, 'minimal' shows plain numbers.
		 */
		variant?: 'gradient' | 'minimal';
	}

	let { deadline, onComplete, variant = 'gradient' }: Props = $props();

	let countdown = $state({ days: 0, hours: 0, minutes: 0, seconds: 0 });
	let interval: ReturnType<typeof setInterval> | null = null;

	function updateCountdown() {
		const now = Date.now();
		const deadlineTime = new Date(deadline).getTime();
		const diff = deadlineTime - now;

		if (diff <= 0) {
			countdown = { days: 0, hours: 0, minutes: 0, seconds: 0 };
			if (interval) {
				clearInterval(interval);
				interval = null;
			}
			onComplete?.();
			return;
		}

		countdown = {
			days: Math.floor(diff / (1000 * 60 * 60 * 24)),
			hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
			minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
			seconds: Math.floor((diff % (1000 * 60)) / 1000)
		};
	}

	onMount(() => {
		updateCountdown();
		interval = setInterval(updateCountdown, 1000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});
</script>

{#if variant === 'gradient'}
	<div class="rounded-xl bg-gradient-to-br from-orange-500 to-pink-500 p-6 text-white">
		<h3 class="mb-4 text-center text-sm font-medium uppercase tracking-wide opacity-90">
			{m.countdown_title()}
		</h3>
		<div class="grid grid-cols-4 gap-2 text-center">
			<div>
				<div class="text-3xl font-bold sm:text-4xl">{countdown.days}</div>
				<div class="text-xs uppercase opacity-75">{m.countdown_days()}</div>
			</div>
			<div>
				<div class="text-3xl font-bold sm:text-4xl">{countdown.hours}</div>
				<div class="text-xs uppercase opacity-75">{m.countdown_hours()}</div>
			</div>
			<div>
				<div class="text-3xl font-bold sm:text-4xl">{countdown.minutes}</div>
				<div class="text-xs uppercase opacity-75">{m.countdown_minutes()}</div>
			</div>
			<div>
				<div class="text-3xl font-bold sm:text-4xl">{countdown.seconds}</div>
				<div class="text-xs uppercase opacity-75">{m.countdown_seconds()}</div>
			</div>
		</div>
	</div>
{:else}
	<!-- Minimal variant -->
	<div class="text-center">
		<h3
			class="mb-6 text-sm font-medium uppercase tracking-widest text-slate-400 dark:text-slate-500"
		>
			{m.countdown_title()}
		</h3>
		<div class="grid grid-cols-4 gap-4 text-center">
			<div>
				<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">
					{countdown.days}
				</div>
				<div
					class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500"
				>
					{m.countdown_days()}
				</div>
			</div>
			<div>
				<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">
					{countdown.hours}
				</div>
				<div
					class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500"
				>
					{m.countdown_hours()}
				</div>
			</div>
			<div>
				<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">
					{countdown.minutes}
				</div>
				<div
					class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500"
				>
					{m.countdown_minutes()}
				</div>
			</div>
			<div>
				<div class="text-5xl font-bold text-slate-800 sm:text-6xl dark:text-white">
					{countdown.seconds}
				</div>
				<div
					class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500"
				>
					{m.countdown_seconds()}
				</div>
			</div>
		</div>
	</div>
{/if}
