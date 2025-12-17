<script lang="ts">
	import * as m from '$lib/paraglide/messages';

	interface Props {
		wishlist: string | null;
		/**
		 * Whether to show the label/title above the wishlist items.
		 */
		showLabel?: boolean;
		/**
		 * Variant: 'default' has background wrapper, 'compact' is just the chips.
		 */
		variant?: 'default' | 'compact';
		/**
		 * Custom label text (uses translation by default).
		 */
		label?: string;
	}

	let { wishlist, showLabel = true, variant = 'default', label }: Props = $props();

	let items = $derived(
		wishlist
			?.split(',')
			.map((w) => w.trim())
			.filter((w) => w.length > 0) ?? []
	);

	let displayLabel = $derived(label ?? m.join_wishlist_title());
</script>

{#if items.length > 0}
	{#if variant === 'default'}
		<div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-700/50">
			{#if showLabel}
				<p
					class="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
				>
					{displayLabel}
				</p>
			{/if}
			<div class="flex flex-wrap justify-center gap-2">
				{#each items as wish (wish)}
					<span
						class="rounded-full bg-white px-3 py-1 text-sm text-slate-700 shadow-sm dark:bg-slate-600 dark:text-slate-200"
					>
						🎁 {wish}
					</span>
				{/each}
			</div>
		</div>
	{:else}
		<!-- Compact variant: no wrapper, smaller chips -->
		<div>
			{#if showLabel}
				<span
					class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
				>
					{displayLabel}:
				</span>
			{/if}
			<div class="mt-1 flex flex-wrap gap-1">
				{#each items as wish (wish)}
					<span
						class="rounded-full bg-white px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-600 dark:text-slate-300"
					>
						🎁 {wish}
					</span>
				{/each}
			</div>
		</div>
	{/if}
{/if}
