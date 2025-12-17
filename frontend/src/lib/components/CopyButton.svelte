<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { createFeedbackState } from '$lib/utils/feedback.svelte';
	import Button from './Button.svelte';
	import { CheckIcon, CopyIcon } from './icons';

	interface Props {
		/** The text to copy to clipboard */
		text: string;
		/** Duration in ms to show success state */
		feedbackDuration?: number;
		/** Button size */
		size?: 'sm' | 'md' | 'lg';
		/** Custom label (defaults to "Copy" / "Copied") */
		label?: string;
		/** Custom copied label */
		copiedLabel?: string;
	}

	let { text, feedbackDuration = 2500, size = 'md', label, copiedLabel }: Props = $props();

	const copied = createFeedbackState(feedbackDuration);

	async function handleCopy() {
		try {
			await navigator.clipboard.writeText(text);
			copied.trigger();
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	let displayLabel = $derived(label ?? m.admin_copy_link());
	let displayCopiedLabel = $derived(copiedLabel ?? m.admin_copied());
</script>

<Button
	variant="outline"
	{size}
	onclick={handleCopy}
	class={copied.active ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600' : ''}
>
	{#if copied.active}
		<CheckIcon class="h-4 w-4" />
	{:else}
		<CopyIcon class="h-4 w-4" />
	{/if}
	<span>{copied.active ? displayCopiedLabel : displayLabel}</span>
</Button>
